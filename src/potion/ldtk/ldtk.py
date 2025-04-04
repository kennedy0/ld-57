import csv
import json
from typing import Iterator

from potion.content import Content
from potion.entity import Entity
from potion.ldtk.ldtk_simplified_int_grid_entity import LDtkSimplifiedIntGridEntity
from potion.ldtk.ldtk_simplified_tiles_entity import LDtkSimplifiedTilesEntity
from potion.level import Level
from potion.log import Log
from potion.scene import Scene
from potion.sprite import Sprite


class LDtk:
    """ Load LDtk project data. """
    @classmethod
    def load_simplified(cls, scene: Scene, content_path: str) -> None:
        """ Load entities into the scene from an LDtk 'Super Simple Export'.
        `content_path` is the path to the *.ldtk project file.
        """
        # Load project data
        with Content.open(content_path) as fp:
            project_data = json.load(fp)

        # Make sure "Super Simple Export" was used
        if not project_data.get('simplifiedExport'):
            Log.error(f"LDtk project must be saved with 'Super Simple Export' mode")
            return

        # Get the simplified folder
        project_folder = Content.parent(content_path)
        project_name = Content.stem(content_path)
        simplified_export_root = f"{project_folder}/{project_name}/simplified"
        if not Content.is_dir(simplified_export_root):
            Log.error(f"Could not find simplified export folder: {simplified_export_root}")
            return

        # Get project info
        world_layout = project_data['worldLayout']

        # Get level names
        level_names = []
        for level_data in project_data['levels']:
            level_names.append(level_data['identifier'])

        level_list: list[Level] = []
        id_to_level_map: dict[str, Level] = {}

        # Build levels
        for level_index, level_name in enumerate(level_names):
            # Get level folder
            level_folder = f"{simplified_export_root}/{level_name}"
            if not Content.is_dir(level_folder):
                Log.error(f"Could not find level folder: {level_folder}")
                continue

            # Load level data
            level_json = f"{level_folder}/data.json"
            if not Content.is_file(level_json):
                Log.error(f"Could not find level data file: {level_json}")
                continue

            with Content.open(level_json) as fp:
                level_data = json.load(fp)

            # Get level info
            level_id = level_data['uniqueIdentifer']
            level_w = level_data['width']
            level_h = level_data['height']

            # Level position is dependent on layout
            if world_layout in ("Free", "GridVania"):
                level_x = level_data['x']
                level_y = level_data['y']
            elif world_layout == "LinearHorizontal":
                if level_index == 0:
                    level_x = 0
                    level_y = 0
                else:
                    previous_level = level_list[level_index-1]
                    level_x = previous_level.x + previous_level.width
                    level_y = 0
            elif world_layout == "LinearVertical":
                if level_index == 0:
                    level_x = 0
                    level_y = 0
                else:
                    previous_level = level_list[level_index - 1]
                    level_x = 0
                    level_y = previous_level.y + previous_level.height
            else:
                Log.error(f"World layout '{world_layout}' is not supported")
                continue

            # Create level
            level = Level(level_name, level_x, level_y, level_w, level_h)
            level.metadata.update({'ldtk_bg_color': level_data['bgColor']})
            level_list.append(level)
            id_to_level_map[level_id] = level
            scene.add_level(level)

            # Build layers
            for layer_index, layer_data in enumerate(project_data['defs']['layers']):
                # Get layer info
                layer_name = layer_data['identifier']
                layer_type = layer_data['type']
                layer_grid_size = layer_data['gridSize']

                # IntGrid
                if layer_type == "IntGrid":
                    # Create entity
                    int_grid = LDtkSimplifiedIntGridEntity()
                    int_grid.name = f"{level_name}-{layer_name}"
                    int_grid.x = level.x
                    int_grid.y = level.y
                    int_grid.z = layer_index
                    int_grid.grid_size = layer_grid_size

                    # Enable collisions
                    if layer_name.lower() in ("collision", "collisions"):
                        int_grid.solid = True
                        int_grid.collisions_enabled = True

                    # Set grid values from csv
                    csv_file = f"{level_folder}/{layer_name}.csv"
                    with Content.open(csv_file) as fp:
                        reader = csv.reader(fp)
                        for y, row in enumerate(reader):
                            for x, cell in enumerate(row):
                                if cell:
                                    value = int(cell)
                                    int_grid.set_value(x, y, value)

                    # Set sprite
                    sprite_file = f"{level_folder}/{layer_name}.png"
                    if Content.exists(sprite_file):
                        int_grid.sprite = Sprite(sprite_file)

                    # Add to level and scene
                    level.add_entity(int_grid)
                    scene.entities.add(int_grid)

                # Entities
                elif layer_type == "Entities":
                    for entity_name, entity_instances in level_data['entities'].items():
                        for instance_data in entity_instances:
                            # Get entity data
                            entity_id = instance_data['iid']
                            entity_x = level.x + instance_data['x']
                            entity_y = level.y + instance_data['y']
                            entity_w = instance_data['width']
                            entity_h = instance_data['height']
                            entity_color = instance_data['color']
                            entity_custom_fields = instance_data['customFields']

                            # Create entity
                            entity = Entity()
                            entity.name = f"{entity_name}-{entity_id}"
                            entity.tags.add("ldtk")
                            entity.tags.add("ldtk_entity")
                            entity.metadata.update({
                                'ldtk_entity_name': entity_name,
                                'ldtk_entity_id': entity_id,
                                'ldtk_entity_color': entity_color,
                                'ldtk_custom_fields': {**entity_custom_fields}
                            })
                            entity.x = entity_x
                            entity.y = entity_y
                            entity.width = entity_w
                            entity.height = entity_h

                            # Set pivot
                            for entity_data in project_data['defs']['entities']:
                                if entity_data['identifier'] == entity_name:
                                    entity.metadata.update({
                                        'ldtk_pivot_x': entity_data['pivotX'],
                                        'ldtk_pivot_y': entity_data['pivotY'],
                                    })
                                    break

                            # Add to level and scene
                            level.add_entity(entity)
                            scene.entities.add(entity)

                # Tiles and AutoLayer
                elif layer_type in ("Tiles", "AutoLayer"):
                    # Create entity
                    tiles = LDtkSimplifiedTilesEntity()
                    tiles.name = f"{level_name}-{layer_name}"
                    tiles.x = level.x
                    tiles.y = level.y
                    tiles.z = layer_index

                    # Set sprite
                    sprite_file = f"{level_folder}/{layer_name}.png"
                    tiles.sprite = Sprite(sprite_file)

                    # Add to level and scene
                    level.add_entity(tiles)
                    scene.entities.add(tiles)

                else:
                    Log.error(f"LDtk layer type '{layer_type}' is not supported")
                    continue

        # Set level depth and neighbors
        previous_level = None
        for level_data in project_data['levels']:
            level_id = level_data['iid']
            level = id_to_level_map[level_id]

            # Set the depth (LDtk world depth is opposite of Potion)
            world_depth = level_data['worldDepth']
            level.depth = -world_depth

            # Set neighbors
            if world_layout in ("Free", "GridVania"):
                for neighbor_data in level_data['__neighbours']:
                    neighbor_id = neighbor_data['levelIid']
                    neighbor_direction = neighbor_data['dir']
                    neighbor_level = id_to_level_map[neighbor_id]
                    if neighbor_direction == "n":
                        level.add_neighbor(neighbor_level, "north")
                    elif neighbor_direction == "s":
                        level.add_neighbor(neighbor_level, "south")
                    elif neighbor_direction == "e":
                        level.add_neighbor(neighbor_level, "east")
                    elif neighbor_direction == "w":
                        level.add_neighbor(neighbor_level, "west")
                    elif neighbor_direction == "ne":
                        level.add_neighbor(neighbor_level, "northeast")
                    elif neighbor_direction == "nw":
                        level.add_neighbor(neighbor_level, "northwest")
                    elif neighbor_direction == "se":
                        level.add_neighbor(neighbor_level, "southeast")
                    elif neighbor_direction == "sw":
                        level.add_neighbor(neighbor_level, "southwest")
                    elif neighbor_direction == ">":
                        level.add_neighbor(neighbor_level, "above")
                    elif neighbor_direction == "<":
                        level.add_neighbor(neighbor_level, "below")
            elif world_layout == "LinearHorizontal":
                if previous_level:
                    previous_level.add_neighbor(level, "east")
                    level.add_neighbor(previous_level, "west")
            elif world_layout == "LinearVertical":
                if previous_level:
                    previous_level.add_neighbor(level, "south")
                    level.add_neighbor(previous_level, "north")

            previous_level = level

        # Force an update of the list so that the entities are in the scene
        # Remember, this will call `awake()`, `on_activate()` and `start()` on all loaded entities
        scene.entities.update_list()

    @classmethod
    def ldtk_entities(cls, scene: Scene) -> Iterator[Entity]:
        """ Iterate over LDtk placeholder entities. """
        for entity in scene.entities:
            if "ldtk_entity" in entity.tags:
                yield entity

    @classmethod
    def swap_entity(cls, ldtk_entity: Entity, entity: Entity) -> None:
        """ Swap an LDtk entity for another entity.
        This is a convenience function to make it easy to swap out the "placeholder" entity from LDtk with a "real" one.
        """
        # Make sure the source entity is an LDtk entity
        if "ldtk_entity" not in ldtk_entity.tags:
            Log.error(f"Not an LDtk entity: {ldtk_entity}")
            return

        # Copy entity data
        entity.x = ldtk_entity.x
        entity.y = ldtk_entity.y
        entity.width = ldtk_entity.width
        entity.height = ldtk_entity.height
        entity.metadata.update(**ldtk_entity.metadata)

        # Swap level membership
        level = ldtk_entity.level
        level.add_entity(entity)
        level.remove_entity(ldtk_entity)

        # Swap scene membership
        scene = ldtk_entity.scene
        scene.entities.add(entity)
        scene.entities.remove(ldtk_entity)
