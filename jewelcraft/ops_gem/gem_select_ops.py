# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2018  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import collections

from bpy.props import EnumProperty, FloatProperty, BoolProperty
from bpy.types import Operator
from bpy.app.translations import pgettext_tip as _

from .. import dynamic_lists


class OBJECT_OT_jewelcraft_select_gems_by_trait(Operator):
    bl_label = "JewelCraft Select Gems By Trait"
    bl_description = "Select gems by trait"
    bl_idname = "object.jewelcraft_select_gems_by_trait"
    bl_options = {"REGISTER", "UNDO"}

    filter_size = BoolProperty(name="Size", options={"SKIP_SAVE"})
    filter_stone = BoolProperty(name="Stone", options={"SKIP_SAVE"})
    filter_cut = BoolProperty(name="Cut", options={"SKIP_SAVE"})
    filter_similar = BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    size = FloatProperty(name="Size", default=1.0, min=0.0, step=10, precision=2, unit="LENGTH")
    stone = EnumProperty(name="Stone", items=dynamic_lists.stones)
    cut = EnumProperty(name="Cut", items=dynamic_lists.cuts)

    def draw(self, context):
        layout = self.layout

        split = layout.split()
        split.prop(self, "filter_size")
        split.prop(self, "size")

        split = layout.split()
        split.prop(self, "filter_stone")
        split.prop(self, "stone", text="")

        split = layout.split()
        split.prop(self, "filter_cut", text="Cut", text_ctxt="JewelCraft")
        split.template_icon_view(self, "cut", show_labels=True)

    def execute(self, context):
        obs = context.visible_objects
        size = round(self.size, 2)

        expr = "for ob in obs:"
        expr += "\n if 'gem' in ob"

        if self.filter_size:
            expr += " and round(ob.dimensions[1], 2) == size"
        if self.filter_stone:
            expr += " and ob['gem']['stone'] == self.stone"
        if self.filter_cut:
            expr += " and ob['gem']['cut'] == self.cut"

        expr += ": ob.select = True"
        expr += "\n else: ob.select = False"

        exec(expr)

        return {"FINISHED"}

    def invoke(self, context, event):
        ob = context.active_object

        if self.filter_similar and ob and "gem" in ob:
            self.filter_size = True
            self.filter_stone = True
            self.filter_cut = True
            self.size = ob.dimensions[1]
            self.stone = ob["gem"]["stone"]
            self.cut = ob["gem"]["cut"]

        return self.execute(context)


class OBJECT_OT_jewelcraft_select_doubles(Operator):
    bl_label = "JewelCraft Select Doubles"
    bl_description = (
        "Select duplicated gems (located in the same spot)\n"
        "WARNING: it does not work with dupli-faces, objects only"
    )
    bl_idname = "object.jewelcraft_select_doubles"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        doubles = collections.defaultdict(list)

        for ob in context.visible_objects:
            ob.select = False

            if "gem" in ob:
                loc = ob.matrix_world.to_translation().to_tuple()
                doubles[loc].append(ob)

        doubles = {k: v for k, v in doubles.items() if len(v) > 1}

        if doubles:
            d = 0

            for obs in doubles.values():
                for ob in obs[:-1]:
                    ob.select = True
                    d += 1

            self.report({"WARNING"}, _("{} duplicates found").format(d))

        else:
            self.report({"INFO"}, _("{} duplicates found").format(0))

        return {"FINISHED"}
