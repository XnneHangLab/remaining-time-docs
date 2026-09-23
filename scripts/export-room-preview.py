"""Export a pinned room-preview snapshot without running the game.

python scripts/export-room-preview.py --repo ../remaining-time --ref <commit>
Only tracked files from the resolved commit are read; working-tree edits are ignored.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def export(repo, ref):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args])

    commit = git('rev-parse', '--verify', ref + '^{commit}').decode().strip()
    files = set(git('ls-tree', '-r', '--name-only', commit).decode().splitlines())

    def raw(path):
        return git('show', f'{commit}:{path}')

    def read(path):
        return json.loads(raw(path))

    recipe = read('art/room-maps.json')
    manifest = read('public/content/remaining-time/manifest.json')
    scenes = [read('public/content/remaining-time/' + p) for p in manifest['scenes']]
    images = {}
    rooms = []
    # Assemble in a temporary directory, so a missing required asset cannot leave a partial export.
    with tempfile.TemporaryDirectory() as temp:
        staging = Path(temp)

        def image(path, optional=False):
            source_path = PurePosixPath(path)
            if source_path.is_absolute() or '..' in source_path.parts or not path.startswith(('public/assets/', 'art/props/')):
                raise ValueError(f'Unsafe image path: {path}')
            if path not in files:
                if optional:
                    return None
                raise ValueError(f'Missing image at {commit}: {path}')
            if path not in images:
                data = raw(path)
                if data[:8] != b'\x89PNG\r\n\x1a\n':
                    raise ValueError(f'Not a PNG: {path}')
                width, height = struct.unpack('>II', data[16:24])
                target = staging / commit / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                images[path] = dict(url=f'/room-preview/{commit}/' + path, width=width, height=height,
                                    sha256=hashlib.sha256(data).hexdigest())
            return path

        def sprite(visual, position, depth, npc=False):
            image_path = image('public/' + visual['image'])
            crop = None
            if npc:
                ident = PurePosixPath(visual['image']).name.removesuffix('-idle.png')
                asset = read(f'public/assets/room-npcs/{ident}.json')
                # initialEntities starts at orientation 90; RoomNpc selects front idle at t=0.
                animation = asset['animations'].get('idle-front', asset['animations']['idle'])
                frame = asset['frames'][animation['frames'][0]]
                crop = [frame['x'], frame['y'], frame['w'], frame['h']]
                visual = {**visual, 'anchor': [frame['anchor'][0] / frame['w'], frame['anchor'][1] / frame['h']]}
                image_path = image(f'public/assets/room-npcs/{ident}.png')
            return dict(visual=visual, position=position, depth=depth, npc=npc, image=image_path, crop=crop)

        for scene in scenes:
            ident = scene['id']
            map_path = f'src/content/remaining-time/{scene["map"]["source"]}'
            game_map = read(map_path)
            if game_map.get('showTiles') or not game_map.get('art'):
                raise ValueError(f'{ident}: tile renderer is not supported by this static art preview')
            layout_file = recipe.get('layoutFiles', {}).get(ident, 'layout.json')
            layout_path = f'public/assets/{ident}/{layout_file}'
            layout = read(layout_path)
            original = image(f'art/props/{ident}/room-layout.png', optional=True)
            variants = {}
            for key, filename in [('plain', 'layout.json'), ('box', 'layout-box.json')]:
                source = f'public/assets/{ident}/{filename}'
                background_name = read(source)['background'] if source in files else ('background-box.png' if key == 'box' else 'background.png')
                variants[key] = image(f'public/assets/{ident}/' + background_name, optional=True)
            background = 'public/' + game_map['art'][0]['image']
            expected = f'public/assets/{ident}/{layout["background"]}'
            active = next((key for key, value in variants.items() if value == background), 'other')
            issues = []
            if background != expected:
                issues.append(f'源配方选择 {layout_file} → {expected}，运行地图实际使用 {background}。')
            if [game_map['width'] * 32, game_map['height'] * 32] != [layout['sourceLayout']['width'], layout['sourceLayout']['height']]:
                issues.append('源布局画布尺寸与运行网格尺寸不同；拼装图以运行网格为准。')
            if not original:
                issues.append('此提交未找到原始完整 PNG。')
            layers = [sprite(art, art['position'], art['depth']) for art in game_map['art']]
            npc_count = 0
            furniture_count = 0
            for entity in scene['entities']:
                visual = entity.get('sprite')
                if not visual:
                    raise ValueError(f'{ident}/{entity["id"]}: unsupported non-sprite entity')
                if entity.get('seatedOn'):
                    raise ValueError(f'{ident}/{entity["id"]}: seated NPC needs an explicit renderer adaptation')
                npc = visual['image'].startswith('assets/room-npcs/')
                npc_count += int(npc)
                furniture_count += int(not npc and not entity.get('portal'))
                points = entity.get('portalTiles', [entity['position']])
                depth = 1 if entity.get('portalTiles') else entity.get('seat', {}).get('depth', entity['position'][1] * 32 + 32)
                layers.extend(sprite(visual, [x * 32, y * 32], depth, npc) for x, y in points)
            rooms.append(dict(id=ident, name=scene['name'], width=game_map['width'] * 32,
                              height=game_map['height'] * 32, original=original, variants=variants,
                              active=active, background=background, layoutSource=layout_path,
                              mapSource=map_path, sceneSource=f'public/content/remaining-time/scenes/{ident}.json',
                              issues=issues, layers=layers, npcCount=npc_count,
                              objectCount=len(game_map['art']) - 1 + furniture_count))
        snapshot = dict(commit=commit, repository='NevaMind-AI/remaining-time',
                        contentVersion=manifest['content_version'], rooms=rooms, images=images)
        # Byte-for-byte copy of the game's placement function (including its validation helper).
        placement = raw('prototype/assets.ts')
        license_text = raw('LICENSE')
        target = ROOT / 'docs/public/room-preview'
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(staging, target)
        generated = ROOT / 'docs/.vitepress/theme/room-preview/generated'
        generated.mkdir(parents=True, exist_ok=True)
        (generated / 'rooms.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        (generated / 'assets.ts').write_bytes(placement)
        (generated / 'LICENSE').write_bytes(license_text)
    print(f'Exported {len(rooms)} rooms / {len(images)} PNGs from {commit}')
    print(f'Runtime: {sum(r["active"] == "box" for r in rooms)} black-frame, '
          f'{sum(r["active"] == "plain" for r in rooms)} original-background rooms')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--ref', required=True)
    args = parser.parse_args()
    export(args.repo, args.ref)
