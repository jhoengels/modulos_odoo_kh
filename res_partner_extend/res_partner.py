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

from osv import osv, fields
import urllib2
import urllib
import cookielib
import re

import logging
_logger = logging.getLogger(__name__)


def get_url(url):
    """Return a string of a get url query"""
    try:
        import urllib
        objfile = urllib.urlopen(url)
        rawfile = objfile.read()
        objfile.close()
        return rawfile
    except ImportError:
        raise Exception ('Error: Unable to import urllib !')
    except IOError:
        raise Exception ('Error: Web Service [%s] does not exist or it is non accesible !' % url)

class res_partner_cookie_reniec(osv.osv):
    _name= 'res.partner.cookie.reniec'
    _columns = {
        'name':fields.char('Codigo', size=4),
        'cookie_reniec': fields.text('Cookie reniec'),
        'urls': fields.char('Enlace',size=200),     
    }

    def open_url(self, cr, uid, ids, context):
        drawing_url = self.browse(cr, uid, ids)[0].urls
        if drawing_url:
            return { 'type': 'ir.actions.act_url', 'url': drawing_url, 'nodestroy': True, 'target': 'new',}
        return True


class res_partner(osv.osv):
    _name= 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'doc_type': fields.selection([('1','DOCUMENTO NACIONAL DE IDENTIDAD (DNI)'),('6','REGISTRO ÚNICO DE CONTRIBUYENTES'),('4','CARNET DE EXTRANJERIA'),('7','PASAPORTE'),('A','CÉDULA DIPLOMÁTICA DE IDENTIDAD'),('0','OTROS TIPOS DE DOCUMENTOS')],'Tipo Doc. Indentidad',required=False,),
        'doc_number': fields.char('Numero Doc. Indentidad',size=32),
        'apellidopaterno': fields.char('Apellido paterno', size=64),
        'apellidomaterno': fields.char('Apellido materno', size=64),
        'nombres': fields.char('Nombres', size=64),
        'codigo_reg_sunat_reniec':fields.char('Codigo', size=4),
    }

    _defaults = {
        'doc_type': '1',
    }

    def onchange_type(self, cr, uid, ids, is_company, doc_type, context=None):
        value = {}
        value['title'] = False
        if is_company:
            domain = {'title': [('domain', '=', 'partner')]}
            value['doc_type'] = '6'
            value['apellidopaterno'] = False
            value['apellidomaterno'] = False
            value['nombres'] = False
        else:
            domain = {'title': [('domain', '=', 'contact')]}
            value['doc_type'] = '1'
        return {'value': value, 'domain': domain}

    def onchange_doc_number(self, cr, uid, ids, doc_type, doc_number, is_company, context=None):
        #response = urllib2.urlopen('http://www.sunat.gob.pe/w/wapS01Alias?ruc=20514540145')
        #html = response.read()
        #url='http://www.sunat.gob.pe/w/wapS01Alias?ruc=20553291501'
        #_logger.error("DOC_TUY: %r", doc_number)
        #str1 = raw_input("NGRESO CODIGO:")
        #_logger.error("DOC_TUY: %r", doc_number)
        res = {'value':{}}
        if doc_number:
            if doc_type in ('6') and len(doc_number) == 11:
                url="http://www.sunat.gob.pe/w/wapS01Alias?ruc="+doc_number
                data = get_url(url)

                res_empres = re.findall('''<small><b>N&#xFA;mero Ruc. </b> \d+ - .* <br/></small>''', data)
                for d in res_empres:
                    name_empresa =  (d[46:-14])
                    #_logger.error("wennnnnnnnn----: %r", name_empresa)
                    import HTMLParser
                    hparser=HTMLParser.HTMLParser()
                    res['value']['name'] = hparser.unescape(hparser.unescape(name_empresa.decode('latin_1')))
        
                res_direcc = re.findall('''<small><b>Direcci&#xF3;n.</b><br/>.*</small><br/>''', data)
                for d in res_direcc:
                    direccion =  (d[34:-13])
                    import HTMLParser
                    hparser=HTMLParser.HTMLParser()
                    res['value']['street'] = hparser.unescape(hparser.unescape(direccion.decode('latin_1')))                 
                return res

            elif doc_type in ('1') and len(doc_number) == 8:
                
                args = []
                #reniec_obj = self.pool.get('res.partner.cookie.reniec')
                #ids = reniec_obj.search(cr, uid, args, offset=0, limit=None, order=None, context=None, count=False)
                img=None
                micookie = None
                #for value in reniec_obj.browse(cr, uid, ids):
                    #img = value.name
                    #micookie = "JSESSIONID="+value.cookie_reniec
                    #_logger.error("MI Cwwwwww: %r", micookie)

                dni= doc_number
                #---------------------
                #dni='42995230'
                #img=codigo_reg_sunat_reniec
                #img='20M7'
                ##url="https://cel.reniec.gob.pe/valreg/valreg.do"

                url = 'http://clientes.reniec.gob.pe/padronElectoral2012/consulta.htm'
                
                micookie = "JSESSIONID=73a8a7d7c3b7d230b0bf5b3a2f730027e17abd7a1a066b3422ab99e5d8163bea.e34MaNqPbN0TaO0Ra3r0"
                #micookie = "JSESSIONID=067492ff835933338624b6077d8f19b91101938e90d89d3d1ea4ee9f64cd0888.e34MaNqPbN0TaO0QaNb0"

                #cookie_j = cookielib.CookieJar()  
                #cookie_h = urllib2.HTTPCookieProcessor(cookie_j)  
                #opener = urllib2.build_opener(cookie_h)  
                #opener.open("https://cel.reniec.gob.pe/valreg/codigo.do")  
                #opener.open("https://cel.reniec.gob.pe/valreg/valreg.do")
                #micookie=None
                #for num, cookie in enumerate(cookie_j):  
                #    micookie=cookie.name + "="+ cookie.value
                #_logger.error("MI COOKIE WEB: %r", micookie)
                #----------------
                
                #data="accion=buscar&tecla_7=5&tecla_8=6&tecla_9=0&tecla_4=4&tecla_5=9&tecla_6=7&tecla_1=2&tecla_2=8&tecla_3=1&tecla_0=3&nuDni="+dni+"&imagen="+img+"&bot_consultar.x=113&bot_consultar.y=16"
                data = "hTipo=2&hDni="+dni+"&hApPat=&hApMat=&hNombre="
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0')
                req.add_header('Cookie',micookie)

                page = urllib2.urlopen(req,data)

                response=page.read();page.close()
                #res_empres = re.findall('''<td height="63" class="style2" align="center">\D+<br>''', response)
                res_empres = re.findall('''<td width="67%" class="txtCuerpo">\D+ </td>''', response)      
                #<td width="67%" class="txtCuerpo">SALAZAR CARLOS, JAVIER HUBER </td>        
                name_empresa = None
                for d in res_empres:
                    name_empres =  (d[34:-6])
                    name_empresa = name_empres.replace(",","")
                    n = name_empresa.split()
                    _logger.error("partner dividido: %r", n[0])   
                    #name_empresa = ' '.join(name_empres.split())
                    import HTMLParser
                    hparser=HTMLParser.HTMLParser()
                    res['value']['name'] = hparser.unescape(name_empresa)
                    res['value']['apellidopaterno'] = n[0]
                    res['value']['apellidomaterno'] = n[1]
                    res['value']['nombres'] = n[2] + ' ' + n[3]


                    #_logger.error("partner -: %r", name_empresa)
    
                #res['value']['name'] = name_empres
                return res
            else:
                res['value']['street'] = False
                res['value']['name'] = False
                res['value']['doc_number'] = False
                return res
        else:
            res['value']['street'] = False
            res['value']['name'] = False
            res['value']['doc_number'] = False
            return res

    def onchange_doc_number_BACKUP(self, cr, uid, ids, doc_type, doc_number, is_company, context=None):
        #response = urllib2.urlopen('http://www.sunat.gob.pe/w/wapS01Alias?ruc=20514540145')
        #html = response.read()
        #url='http://www.sunat.gob.pe/w/wapS01Alias?ruc=20553291501'
        #_logger.error("DOC_TUY: %r", doc_number)
        #str1 = raw_input("NGRESO CODIGO:")
        #_logger.error("DOC_TUY: %r", str1)
        res = {'value':{}}
        if doc_number:
            if doc_type in ('6') and len(doc_number) == 11:
                url="http://www.sunat.gob.pe/w/wapS01Alias?ruc="+doc_number
                data = get_url(url)

                res_empres = re.findall('''<small><b>N&#xFA;mero Ruc. </b> \d+ - .* <br/></small>''', data)
                for d in res_empres:
                    name_empresa =  (d[46:-14])
                    _logger.error("wennnnnnnnn----: %r", name_empresa)
                    import HTMLParser
                    hparser=HTMLParser.HTMLParser()
                    res['value']['name'] = hparser.unescape(hparser.unescape(name_empresa.decode('latin_1')))
        
                res_direcc = re.findall('''<small><b>Direcci&#xF3;n.</b><br/>.*</small><br/>''', data)
                for d in res_direcc:
                    direccion =  (d[34:-13])
                    import HTMLParser
                    hparser=HTMLParser.HTMLParser()
                    res['value']['street'] = hparser.unescape(hparser.unescape(direccion.decode('latin_1')))                 
                return res
            elif doc_type in ('1') and len(doc_number) == 8:

                
                args = []
                reniec_obj = self.pool.get('res.partner.cookie.reniec')
                ids = reniec_obj.search(cr, uid, args, offset=0, limit=None, order=None, context=None, count=False)
                img=None
                micookie = None
                for value in reniec_obj.browse(cr, uid, ids):
                    img = value.name
                    micookie = "JSESSIONID="+value.cookie_reniec
                    #_logger.error("MI Cwwwwww: %r", micookie)

                dni= doc_number
                #---------------------
                #dni='42995230'
                #img=codigo_reg_sunat_reniec
                #img='20M7'
                url="https://cel.reniec.gob.pe/valreg/valreg.do"
                
                #micookie="JSESSIONID=97657851ce58c6a187eb98c45b3af7caaa9519ed812.mALvn6iL-B9zpAzzmMTBpQ8Iq6iUaNaKahD3lN4PagSLa34Iah8K-xuL-AeSa69zaMSLa6aPa64Obh0QawSHc30Ka2bEaAjzawTwp65ynh4IqAjIokjx-ArJmwTKngaLc3iPaN8Sax8xf2bQmkLMnkqxn6jAmljGr5XDqQLvpAe_"

                #cookie_j = cookielib.CookieJar()  
                #cookie_h = urllib2.HTTPCookieProcessor(cookie_j)  
                #opener = urllib2.build_opener(cookie_h)  
                #opener.open("https://cel.reniec.gob.pe/valreg/codigo.do")  
                #opener.open("https://cel.reniec.gob.pe/valreg/valreg.do")
                #micookie=None
                #for num, cookie in enumerate(cookie_j):  
                #    micookie=cookie.name + "="+ cookie.value
                #_logger.error("MI COOKIE WEB: %r", micookie)
                #----------------
                
                #data="accion=buscar&tecla_7=5&tecla_8=6&tecla_9=0&tecla_4=4&tecla_5=9&tecla_6=7&tecla_1=2&tecla_2=8&tecla_3=1&tecla_0=3&nuDni="+dni+"&imagen="+img+"&bot_consultar.x=113&bot_consultar.y=16"
                data="accion=buscar&tecla_7=5&tecla_8=2&tecla_9=0&tecla_4=1&tecla_5=6&tecla_6=9&tecla_1=8&tecla_2=7&tecla_3=3&tecla_0=4&nuDni="+dni+"&imagen="+img+"&bot_consultar.x=75&bot_consultar.y=23"
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0')
                req.add_header('Cookie',micookie)
                page = urllib2.urlopen(req,data)
                response=page.read();page.close()
                res_empres = re.findall('''<td height="63" class="style2" align="center">\D+<br>''', response)
                name_empresa = None
                for d in res_empres:
                    name_empres =  (d[66:-4])
                    n = name_empres.split()    
                    name_empresa = ' '.join(name_empres.split())
                    import HTMLParser
                    hparser=HTMLParser.HTMLParser()
                    res['value']['name'] = hparser.unescape(hparser.unescape(name_empresa.decode('latin_1')))

                    _logger.error("partner -: %r", res['value']['name'])
    
                #res['value']['name'] = name_empresa
                return res
            else:
                res['value']['street'] = False
                res['value']['name'] = False
                #res['value']['doc_number'] = False
                return res
        else:
            #res['value']['street'] = False
            #res['value']['name'] = False
            #res['value']['doc_number'] = False
            return res


    def onchange_cod(self, cr, uid, ids, doc_type, doc_number,codigo_reg_sunat_reniec, is_company, context=None):

        #Inicializamos un objeto que nos servira para poder abrir conexiones con una pagina 
        #y poder guardar las coiokies que nos mande esta pagina
        args = []
        reniec_obj = self.pool.get('res.partner.cookie.reniec')
        ids = reniec_obj.search(cr, uid, args, offset=0, limit=None, order=None, context=None, count=False)
        img=None
        micookie = None
        for value in reniec_obj.browse(cr, uid, ids):
            img = value.name
            micookie = "JSESSIONID="+value.cookie_reniec
            _logger.error("MI Cwwwwww: %r", micookie)



        dni= doc_number
        #dni='42995230'
        #img=codigo_reg_sunat_reniec
        #img='20M7'
        url="https://cel.reniec.gob.pe/valreg/valreg.do"
        
        #micookie="JSESSIONID=97657851ce58c6a187eb98c45b3af7caaa9519ed812.mALvn6iL-B9zpAzzmMTBpQ8Iq6iUaNaKahD3lN4PagSLa34Iah8K-xuL-AeSa69zaMSLa6aPa64Obh0QawSHc30Ka2bEaAjzawTwp65ynh4IqAjIokjx-ArJmwTKngaLc3iPaN8Sax8xf2bQmkLMnkqxn6jAmljGr5XDqQLvpAe_"

        #cookie_j = cookielib.CookieJar()  
        #cookie_h = urllib2.HTTPCookieProcessor(cookie_j)  
        #opener = urllib2.build_opener(cookie_h)  
        #opener.open("https://cel.reniec.gob.pe/valreg/codigo.do")  
        #opener.open("https://cel.reniec.gob.pe/valreg/valreg.do")
        #micookie=None
        #for num, cookie in enumerate(cookie_j):  
        #    micookie=cookie.name + "="+ cookie.value
        #_logger.error("MI COOKIE WEB: %r", micookie)

        data="accion=buscar&tecla_7=5&tecla_8=6&tecla_9=0&tecla_4=4&tecla_5=9&tecla_6=7&tecla_1=2&tecla_2=8&tecla_3=1&tecla_0=3&nuDni="+dni+"&imagen="+img+"&bot_consultar.x=113&bot_consultar.y=16"
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0')
        req.add_header('Cookie',micookie)
        page = urllib2.urlopen(req,data)
        response=page.read();page.close()
        res_empres = re.findall('''<td height="63" class="style2" align="center">\D+<br>''', response)
        name_empresa = None
        for d in res_empres:
            name_empres =  (d[66:-4])
            n = name_empres.split()    
            name_empresa = ' '.join(name_empres.split())
            _logger.error("partner ------: %r", name_empresa)
	
        value = {}
        value['name'] = name_empresa
        return {'value': value}
    
    def onchange_doc_type(self, cr, uid, ids, doc_type, doc_number, is_company, context=None):
        value = {}
        value['doc_number'] = False
        value['name'] = False
        value['street'] = False
        value['apellidopaterno'] = False
        value['apellidomaterno'] = False
        value['nombres'] = False

        #if doc_type in ('6'):
        #    value['is_company'] = True
        #if doc_type in ('1'):
        #    value['is_company'] = True

        return {'value': value}

    def onchange_person(self, cr, uid, ids, name, nombres, apellidopaterno, apellidomaterno, context=None):
        #res = {'value':{}}
        #res['value']['name'] = (apellidopaterno and (apellidopaterno+' ') or '') + (apellidomaterno and (apellidomaterno+' ') or '') + (nombres and (nombres+' ') or '')
        #return res
        return True
