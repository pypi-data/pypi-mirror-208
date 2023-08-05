# Generated by Django 4.0.8 on 2022-11-29 16:34

import django.contrib.postgres.fields
import django.core.serializers.json
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import taggit.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("extras", "0077_customlink_extend_text_and_url"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Application",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, null=True),
                ),
                (
                    "last_updated",
                    models.DateTimeField(auto_now=True, null=True),
                ),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("comments", models.TextField(blank=True)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="ObjectAliasTarget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("target_id", models.PositiveBigIntegerField()),
                (
                    "target_type",
                    models.ForeignKey(
                        limit_choices_to=models.Q(
                            models.Q(
                                models.Q(
                                    ("app_label", "ipam"), ("model", "prefix")
                                ),
                                models.Q(
                                    ("app_label", "ipam"), ("model", "iprange")
                                ),
                                models.Q(
                                    ("app_label", "ipam"),
                                    ("model", "ipaddress"),
                                ),
                                _connector="OR",
                            )
                        ),
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "ordering": ("target_id",),
            },
        ),
        migrations.CreateModel(
            name="ObjectAlias",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, null=True),
                ),
                (
                    "last_updated",
                    models.DateTimeField(auto_now=True, null=True),
                ),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "size",
                    models.PositiveSmallIntegerField(
                        default=0, editable=False
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
                (
                    "targets",
                    models.ManyToManyField(
                        related_name="aliases",
                        to="netbox_data_flows.objectaliastarget",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="DataFlowGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, null=True),
                ),
                (
                    "last_updated",
                    models.DateTimeField(auto_now=True, null=True),
                ),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("comments", models.TextField(blank=True)),
                ("status", models.CharField(default="enabled", max_length=10)),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                (
                    "tree_id",
                    models.PositiveIntegerField(db_index=True, editable=False),
                ),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "application",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dataflow_groups",
                        to="netbox_data_flows.application",
                    ),
                ),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="netbox_data_flows.dataflowgroup",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
            ],
            options={
                "ordering": ("application", "name"),
            },
        ),
        migrations.CreateModel(
            name="DataFlow",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, null=True),
                ),
                (
                    "last_updated",
                    models.DateTimeField(auto_now=True, null=True),
                ),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.CharField(blank=True, max_length=500)),
                ("comments", models.TextField(blank=True)),
                ("status", models.CharField(default="enabled", max_length=10)),
                ("protocol", models.CharField(max_length=10)),
                (
                    "source_ports",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.PositiveIntegerField(
                            validators=[
                                django.core.validators.MinValueValidator(1),
                                django.core.validators.MaxValueValidator(
                                    65535
                                ),
                            ]
                        ),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "destination_ports",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.PositiveIntegerField(
                            validators=[
                                django.core.validators.MinValueValidator(1),
                                django.core.validators.MaxValueValidator(
                                    65535
                                ),
                            ]
                        ),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "application",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dataflows",
                        to="netbox_data_flows.application",
                    ),
                ),
                (
                    "destinations",
                    models.ManyToManyField(
                        related_name="dataflow_destinations",
                        to="netbox_data_flows.objectalias",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dataflows",
                        to="netbox_data_flows.dataflowgroup",
                    ),
                ),
                (
                    "sources",
                    models.ManyToManyField(
                        related_name="dataflow_sources",
                        to="netbox_data_flows.objectalias",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
            ],
            options={
                "ordering": ("application", "group", "name"),
            },
        ),
        migrations.CreateModel(
            name="ApplicationRole",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, null=True),
                ),
                (
                    "last_updated",
                    models.DateTimeField(auto_now=True, null=True),
                ),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="application",
            name="role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="applications",
                to="netbox_data_flows.applicationrole",
            ),
        ),
        migrations.AddField(
            model_name="application",
            name="tags",
            field=taggit.managers.TaggableManager(
                through="extras.TaggedItem", to="extras.Tag"
            ),
        ),
        migrations.AddConstraint(
            model_name="objectaliastarget",
            constraint=models.UniqueConstraint(
                fields=("target_type", "target_id"),
                name="netbox_data_flows_objectaliastarget_type_id",
            ),
        ),
        migrations.AddConstraint(
            model_name="dataflowgroup",
            constraint=models.UniqueConstraint(
                fields=("parent", "name"),
                name="netbox_data_flows_dataflowgroup_parent_name",
            ),
        ),
        migrations.AddConstraint(
            model_name="dataflowgroup",
            constraint=models.UniqueConstraint(
                condition=models.Q(("parent", None)),
                fields=("application", "name"),
                name="netbox_data_flows_dataflowgroup_application_name",
            ),
        ),
    ]
