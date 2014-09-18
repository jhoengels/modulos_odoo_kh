# -*- encoding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (c) 2014 KIDDYS HOUSE SAC. (http://kiddyshouse.com).
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

from osv import osv, fields
import netsvc
from tools.translate import _
import decimal_precision as dp



class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'ruc_dni': fields.char('RUC/DNI',size=32, states={'manual':[('readonly',True)], 'progress':[('readonly',True)],'done':[('readonly',True)]})
        }

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False, 'ruc_dni': False}}

        val = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context)
        value = val['value']
        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        value.update({
               'ruc_dni': part.doc_number,
            })
        return {'value': value}

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        if context is None:
            context = {}

        invoice_vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context)
        invoice_vals.update({
                'ruc_dni': order.ruc_dni or '', #agregado nuevos cambios
            })

        return invoice_vals
    
    def onchange_ruc_dni(self, cr, uid, ids, ruc_dni, context=None):
        if context is None:
            context = {}
        value = {}
        partner_obj = self.pool.get('res.partner')
        if ruc_dni:
            partner_id = partner_obj.search(cr,uid,[('doc_number','=',ruc_dni)])
            if partner_id:
                value.update({
                       'partner_id': partner_id,
                    })
                return {'value': value}
            else:
                raise osv.except_osv(_('Warning!'), _('Usuario no registrado en el sistema.'))
        else:            
            return {'value': {'partner_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False, 'ruc_dni': False}}

sale_order()



class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
	'ruc_dni': fields.char('RUC/DNI',size=32,states={'manual':[('readonly',True)], 'progress':[('readonly',True)],'done':[('readonly',True)]})
        }

    def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        val =  super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        result = val['value']
        p = self.pool.get('res.partner').browse(cr, uid, partner_id)
        result.update({
               'ruc_dni': p.doc_number,# agregado nuevos cambios
            })
        return {'value': result} 

account_invoice()

