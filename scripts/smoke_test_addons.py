# Smoke test dos addons de inventario e RH (rodar via odoo shell)
from odoo import fields

print("=== MODULOS ===")
mods = env["ir.module.module"].search(
    [
        (
            "name",
            "in",
            [
                "stock",
                "stock_request",
                "hr",
                "hr_personal_equipment_request",
                "hr_employee_ppe",
            ],
        )
    ]
)
for m in mods:
    print("%s -> %s" % (m.name, m.state))
assert all(m.state == "installed" for m in mods), "Modulos nao instalados"

print("=== STOCK REQUEST ===")
product = env["product.product"].search([("type", "=", "product")], limit=1)
wh = env["stock.warehouse"].search([], limit=1)
assert product and wh, "Falta produto storable ou warehouse (demo)"
sr = env["stock.request"].create(
    {
        "product_id": product.id,
        "product_uom_id": product.uom_id.id,
        "product_uom_qty": 1.0,
        "warehouse_id": wh.id,
        "location_id": wh.lot_stock_id.id,
        "expected_date": fields.Datetime.now(),
    }
)
sr.action_confirm()
print("stock.request %s state=%s" % (sr.name, sr.state))
assert sr.state in ("open", "done"), "Confirmacao do stock.request falhou"

print("=== HR PPE / PERSONAL REQUEST ===")
ppe_tmpl = env["product.template"].create(
    {
        "name": "Capacete EPI teste",
        "type": "consu",
        "is_personal_equipment": True,
        "is_ppe": True,
        "indications": "Obrigatorio em area de risco",
        "expirable_ppe": True,
        "ppe_duration": 12,
        "ppe_interval_type": "months",
    }
)
ppe = env["product.product"].search([("product_tmpl_id", "=", ppe_tmpl.id)], limit=1)
employee = env["hr.employee"].search([], limit=1)
assert employee, "Falta funcionario demo"
req = env["hr.personal.equipment.request"].create(
    {
        "employee_id": employee.id,
        "observations": "Smoke test EPI",
        "line_ids": [
            (
                0,
                0,
                {
                    "product_id": ppe.id,
                    "quantity": 1,
                    "product_uom_id": ppe.uom_id.id,
                },
            )
        ],
    }
)
req.accept_request()
print(
    "hr.personal.equipment.request id=%s state=%s lines=%s"
    % (req.id, req.state, len(req.line_ids))
)
assert req.state == "accepted", "Aceite do pedido de EPI falhou"
assert ppe_tmpl.is_ppe, "Flag is_ppe ausente"
print("OK")
env.cr.commit()
