#!/usr/bin/env python3
import argparse
import logging
import pathlib
import random
import shutil
import sys
from watchtower_pipeline import writers, models

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def create_example_project():
    # Create Users
    users_list = []
    for i in range(10):
        user = models.User(name=f"User {i}")
        users_list.append(user)

    # Create Asset Types
    asset_types_list = []
    for n in ['Characters', 'Props', 'Environment', 'FX']:
        asset_type = models.AssetType(name=n)
        asset_types_list.append(asset_type)

    task_types_list = []
    for n, c in [
        ('Concept', '#8D6E63'),
        ('Modeling', '#78909C'),
        ('Shading', '#64B5F6'),
        ('Rigging', '#9CCC65'),
    ]:
        task_type = models.TaskType(
            name=n,
            color=c,
            for_shots=False,
        )
        task_types_list.append(task_type)
    for n, c in [
        ('Storyboard', '#43A047'),
        ('Layout', '#7CB342'),
        ('Animation', '#F9A825'),
        ('Lighting', '#9CCC65'),
    ]:
        task_type = models.TaskType(
            name=n,
            color=c,
            for_shots=True,
        )
        task_types_list.append(task_type)

    task_statuses_list = []
    for n, c in [
        ('Todo', '#f5f5f5'),
        ('Work In Progress', '#3273dc'),
        ('Done', '#22d160'),
    ]:
        task_status = models.TaskStatus(id=None, name=n, color=c)
        task_statuses_list.append(task_status)

    project = models.Project(
        id='example-project-uuid',
        name='Example Project',
        ratio="2.35:1",
        resolution='2018x858',
        asset_types=[],
        task_types=[],
        task_statuses=[],
        team=[p.id for p in users_list],
        thumbnailUrl=f"https://picsum.photos/id/{10}/192/108",
    )

    context_writer = writers.ContextWriter(
        projects=[project],
        asset_types=asset_types_list,
        task_types=task_types_list,
        task_status=task_statuses_list,
        users=users_list,
    )

    context_writer.download_previews()
    context_writer.write_as_json()

    # Create Assets
    assets_list = []
    for i in range(10):
        asset_type = random.choice(asset_types_list)
        asset = models.Asset(
            name=f"Asset {i}",
            asset_type_id=asset_type.id,
            thumbnailUrl=f"https://picsum.photos/id/{i + 1}/192/108",
        )
        for t in range(3):
            rand_task_status = random.choice(task_statuses_list)
            random_task_type = random.choice(
                [tt for tt in task_types_list if tt.for_shots is False]
            )
            random_user = random.choice(users_list)
            asset.tasks.append(
                models.Task(
                    rand_task_status.id,
                    random_task_type.id,
                    [random_user.id],
                )
            )
        assets_list.append(asset)
    # Create a single Sequence
    sequence = models.Sequence(name='Seq 1')
    sequences_list = [sequence]
    # Create Shots
    shots_list = []
    frame_in = 0
    frame_out = 50
    for i in range(20):
        shot = models.Shot(
            name=f"SH_{i+1}",
            sequence_id=sequence.id,
            data=models.ShotData(frame_in=frame_in, frame_out=frame_out),
            thumbnailUrl=f"https://picsum.photos/id/{i+1}/192/108",
        )
        for t in range(4):
            rand_task_status = random.choice(task_statuses_list)
            random_task_type = random.choice([tt for tt in task_types_list if tt.for_shots is True])
            random_user = random.choice(users_list)
            shot.tasks.append(
                models.Task(
                    rand_task_status.id,
                    random_task_type.id,
                    [random_user.id],
                )
            )
        frame_in = frame_out
        frame_out += random.randint(20, 150)
        shots_list.append(shot)

    # Casting
    shot_castings = []
    for s in shots_list:
        shot_castings.append(models.ShotCasting(shot=s, assets=random.sample(assets_list, 3)))

    # Create Edit
    edit = models.Edit(
        project=project,
        totalFrames=frame_out,
        frameOffset=20,
    )

    project_writer = writers.ProjectWriter(
        project=project,
        shots=shots_list,
        assets=assets_list,
        sequences=sequences_list,
        edit=edit,
        casting=shot_castings,
    )

    project_writer.download_previews()
    project_writer.write_as_json()

    static_path_dst = pathlib.Path().cwd().absolute() / 'public/static'
    logging.info(f"Data downloaded in {static_path_dst}")
    return static_path_dst


def main(args):
    parser = argparse.ArgumentParser(description="Generate example  Watchtower content.")
    parser.add_argument("-b", "--bundle", action=argparse.BooleanOptionalAction)
    args = parser.parse_args(args)

    static_path = create_example_project()
    if args.bundle:
        writers.WatchtowerBundler.bundle(static_path)
        shutil.rmtree(static_path.parent)


if __name__ == "__main__":
    main(sys.argv[1:])
