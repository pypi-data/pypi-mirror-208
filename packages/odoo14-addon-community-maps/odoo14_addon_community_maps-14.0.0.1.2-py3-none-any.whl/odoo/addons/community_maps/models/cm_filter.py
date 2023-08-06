from odoo import models, api, fields
from odoo.tools.translate import _


class CmFilter(models.Model):
    _name = "cm.filter"

    _inherit = ["cm.slug.id.mixin"]

    name = fields.Char(string=_("Name"), translate=True)
    icon = fields.Char(string=_("Icon"))
    color = fields.Char(string=_("Color"))
    marker_color = fields.Char(string=_("Marker main color (hex)"))
    marker_text_color = fields.Char(string=_("Marker text color (hex)"))
    marker_bg_color = fields.Char(string=_("Marker background color (hex)"))
    marker_border_color = fields.Char(string=_("Marker border color (hex)"))
    description = fields.Char(string=_("Description"), translate=True)
    filter_group_id = fields.Many2one("cm.filter.group", string="Filter Group")
    places_mids = fields.Many2many(
        "cm.place",
        "cm_places_filters",
        "filter_id",
        "place_id",
        string=_("Related places"),
    )

    def get_datamodel_dict(self):
        datamodel = {
            "slug": self.slug_id,
            "name": self.name,
            "iconKey": None,
            "iconColor": None,
            "markerColor": {
                "markerText": self.marker_text_color,
                "markerColor": self.marker_color,
                "markerBg": self.marker_bg_color,
                "markerBorder": self.marker_border_color
            },
            "description": None,
        }
        if self.icon:
            datamodel["iconKey"] = self.icon
        if self.color:
            datamodel["iconColor"] = self.color
        if self.description:
            datamodel["description"] = self.description
        return datamodel
