# -*- coding: utf-8 -*-
import unittest
from email.header import Header
from openprocurement.tender.competitivedialogue.tests.base import (BaseCompetitiveDialogUAContentWebTest,
                                                                   BaseCompetitiveDialogEUContentWebTest)


class DialogEUDocumentResourceTest(BaseCompetitiveDialogEUContentWebTest):
    docservice = False

    initial_auth = ('Basic', ('broker', ''))

    def test_not_found(self):
        """ Test not found """
        # Try get documents by bad dialog id
        response = self.app.get('/tenders/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try create document by bad dialog id
        response = self.app.post('/tenders/some_id/documents',
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try create document with invalid_field
        response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token),
                                 status=404, upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        # Try put document by bad dialog id, and document id
        response = self.app.put('/tenders/some_id/documents/some_id',
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try put documents by bad document_id
        response = self.app.put('/tenders/{}/documents/some_id?acc_token={}'.format(self.tender_id, self.tender_token),
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

        # Try get document by bad dialog id, and documents id
        response = self.app.get('/tenders/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try get document by bad document id
        response = self.app.get('/tenders/{}/documents/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_document(self):
        """
          Test create dialog document
        """
        # Get empty list of documents
        response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json, {"data": []})

        # Create document, and save doc_id, and key
        response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token),
                                 upload_files=[('file', u'укр.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        if self.docservice:
            self.assertIn('Signature=', response.json["data"]["url"])
            self.assertIn('KeyID=', response.json["data"]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
            key = response.json["data"]["url"].split('/')[-1].split('?')[0]
            tender = self.db.get(self.tender_id)
            self.assertIn(key, tender['documents'][-1]["url"])
            self.assertIn('Signature=', tender['documents'][-1]["url"])
            self.assertIn('KeyID=', tender['documents'][-1]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
        else:
            key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        # Try get documents
        response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual(u'укр.doc', response.json["data"][0]["title"])

        # Try get document with bad download param
        response = self.app.get('/tenders/{}/documents/{}?download=some_id'.format(
            self.tender_id, doc_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        if self.docservice:
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(
                self.tender_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertNotIn('Expires=', response.location)
        else:
            # Get document and check response fields
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(self.tender_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 7)
            self.assertEqual(response.body, 'content')

        # Get document and check response fields
        response = self.app.get('/tenders/{}/documents/{}'.format(self.tender_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])

        # Create new document with Ukrainian descriptions
        response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token),
                                 upload_files=[('file', u'укр.doc'.encode("ascii", "xmlcharrefreplace"), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertNotIn('acc_token', response.headers['Location'])

    def test_put_tender_document(self):
        """
          Test put dialog document
        """
        from six import BytesIO
        from urllib import quote
        # Try create document without acc_token
        body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename={}\nContent-Type: application/msword\n\ncontent\n'''.format(u'\uff07')
        environ = self.app._make_environ()
        environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
        environ['REQUEST_METHOD'] = 'POST'
        req = self.app.RequestClass.blank(self.app._remove_fragment('/tenders/{}/documents'.format(self.tender_id)),
                                          environ)
        req.environ['wsgi.input'] = BytesIO(body.encode('utf8'))
        req.content_length = len(body)
        response = self.app.do_request(req, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "could not decode params")

        # Create document
        body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename*=utf-8''{}\nContent-Type: application/msword\n\ncontent\n'''.format(quote('укр.doc'))
        environ = self.app._make_environ()
        environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
        environ['REQUEST_METHOD'] = 'POST'
        req = self.app.RequestClass.blank(self.app._remove_fragment('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token)), environ)
        req.environ['wsgi.input'] = BytesIO(body.encode(req.charset or 'utf8'))
        req.content_length = len(body)
        response = self.app.do_request(req)
        #response = self.app.post('/tenders/{}/documents'.format(
            #self.tender_id), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        self.assertIn(doc_id, response.headers['Location'])

        # Update document
        response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, self.tender_token),
                                upload_files=[('file', 'name  name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        if self.docservice:
            self.assertIn('Signature=', response.json["data"]["url"])
            self.assertIn('KeyID=', response.json["data"]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
            key = response.json["data"]["url"].split('/')[-1].split('?')[0]
            tender = self.db.get(self.tender_id)
            self.assertIn(key, tender['documents'][-1]["url"])
            self.assertIn('Signature=', tender['documents'][-1]["url"])
            self.assertIn('KeyID=', tender['documents'][-1]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
        else:
            key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        # Get document
        if self.docservice:
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(
                self.tender_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertNotIn('Expires=', response.location)
        else:
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(
                self.tender_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content2')

        # Get document and check response fields
        response = self.app.get('/tenders/{}/documents/{}'.format(self.tender_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name name.doc', response.json["data"]["title"])
        dateModified2 = response.json["data"]['dateModified']
        self.assertTrue(dateModified < dateModified2)
        self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])

        # Get documents with uri param all=true
        response = self.app.get('/tenders/{}/documents?all=true'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified2, response.json["data"][1]['dateModified'])

        # Create new documents, save doc_id, dateModified
        response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        self.assertIn(doc_id, response.headers['Location'])

        # Get documents, and check dateModified
        response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified2, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified, response.json["data"][1]['dateModified'])

        # Try update documents with ivalid fields
        response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, self.tender_token),
                                status=404, upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        # Update document
        response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, self.tender_token),
                                'content3', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        if self.docservice:
            self.assertIn('Signature=', response.json["data"]["url"])
            self.assertIn('KeyID=', response.json["data"]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
            key = response.json["data"]["url"].split('/')[-1].split('?')[0]
            tender = self.db.get(self.tender_id)
            self.assertIn(key, tender['documents'][-1]["url"])
            self.assertIn('Signature=', tender['documents'][-1]["url"])
            self.assertIn('KeyID=', tender['documents'][-1]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
        else:
            key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        # Get document and check response fields
        if self.docservice:
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(self.tender_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertNotIn('Expires=', response.location)
        else:
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(self.tender_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content3')

    def test_patch_tender_document(self):
        """
          Test path dialog document
        """
        # Create documents, check response fields and save doc_id
        response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token),
                                 upload_files=[('file', str(Header(u'укр.doc', 'utf-8')), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])

        # Try connect document with lot, without description in params
        response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                      doc_id,
                                                                                      self.tender_token),
                                       {"data": {"documentOf": "lot"}},
                                       status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedItem'},
        ])

        # Try connect document with lot, by bad relatedItem
        response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                      doc_id,
                                                                                      self.tender_token),
                                       {'data': {'documentOf': 'lot', 'relatedItem': '0' * 32}},
                                       status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
        ])

        # Try connect document with item, by bad relatedItem
        response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                      doc_id,
                                                                                      self.tender_token),
                                       {'data': {'documentOf': 'item', 'relatedItem': '0' * 32}},
                                       status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of items'], u'location': u'body', u'name': u'relatedItem'}
        ])

        # Update description in document
        response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                      doc_id,
                                                                                      self.tender_token),
                                       {"data": {"description": "document description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        # Get document and check description
        response = self.app.get('/tenders/{}/documents/{}'.format(self.tender_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])


class DialogEUDocumentWithDSResourceTest(DialogEUDocumentResourceTest):
    docservice = True


class DialogUADocumentResourceTest(BaseCompetitiveDialogUAContentWebTest):
    docservice = False

    initial_auth = ('Basic', ('broker', ''))

    def test_not_found(self):
        """ Test not found """
        # Try get documents by bad dialog id
        response = self.app.get('/tenders/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try create document by bad dialog id
        response = self.app.post('/tenders/some_id/documents',
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try create document with invalid_field
        response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token),
                                 status=404, upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        # Try put document by bad dialog id, and document id
        response = self.app.put('/tenders/some_id/documents/some_id',
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try put documents by bad document_id
        response = self.app.put('/tenders/{}/documents/some_id?acc_token={}'.format(self.tender_id, self.tender_token),
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

        # Try get document by bad dialog id, and documents id
        response = self.app.get('/tenders/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try get document by bad document id
        response = self.app.get('/tenders/{}/documents/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_document(self):
        """
          Test create dialog document
        """
        # Get empty list of documents
        response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json, {"data": []})

        # Create document, and save doc_id, and key
        response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token),
                                 upload_files=[('file', u'укр.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        if self.docservice:
            self.assertIn('Signature=', response.json["data"]["url"])
            self.assertIn('KeyID=', response.json["data"]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
            key = response.json["data"]["url"].split('/')[-1].split('?')[0]
            tender = self.db.get(self.tender_id)
            self.assertIn(key, tender['documents'][-1]["url"])
            self.assertIn('Signature=', tender['documents'][-1]["url"])
            self.assertIn('KeyID=', tender['documents'][-1]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
        else:
            key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        # Try get documents
        response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual(u'укр.doc', response.json["data"][0]["title"])

        # Try get document with bad download param
        response = self.app.get('/tenders/{}/documents/{}?download=some_id'.format(self.tender_id, doc_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        if self.docservice:
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(
                self.tender_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertNotIn('Expires=', response.location)
        else:

            # Get document and check response fields
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(self.tender_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 7)
            self.assertEqual(response.body, 'content')

        # Get document and check response fields
        response = self.app.get('/tenders/{}/documents/{}'.format(self.tender_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])

        # Create new document with Ukrainian descriptions
        response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token),
                                 upload_files=[('file', u'укр.doc'.encode("ascii", "xmlcharrefreplace"), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertNotIn('acc_token', response.headers['Location'])

    def test_put_tender_document(self):
        """
          Test put dialog document
        """
        from six import BytesIO
        from urllib import quote
        # Try create document without acc_token
        body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename={}\nContent-Type: application/msword\n\ncontent\n'''.format(u'\uff07')
        environ = self.app._make_environ()
        environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
        environ['REQUEST_METHOD'] = 'POST'
        req = self.app.RequestClass.blank(self.app._remove_fragment('/tenders/{}/documents'.format(self.tender_id)),
                                          environ)
        req.environ['wsgi.input'] = BytesIO(body.encode('utf8'))
        req.content_length = len(body)
        response = self.app.do_request(req, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "could not decode params")

        # Create document
        body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename*=utf-8''{}\nContent-Type: application/msword\n\ncontent\n'''.format(quote('укр.doc'))
        environ = self.app._make_environ()
        environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
        environ['REQUEST_METHOD'] = 'POST'
        req = self.app.RequestClass.blank(self.app._remove_fragment('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token)), environ)
        req.environ['wsgi.input'] = BytesIO(body.encode(req.charset or 'utf8'))
        req.content_length = len(body)
        response = self.app.do_request(req)
        #response = self.app.post('/tenders/{}/documents'.format(
            #self.tender_id), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        self.assertIn(doc_id, response.headers['Location'])

        # Update document
        response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, self.tender_token),
                                upload_files=[('file', 'name  name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        if self.docservice:
            self.assertIn('Signature=', response.json["data"]["url"])
            self.assertIn('KeyID=', response.json["data"]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
            key = response.json["data"]["url"].split('/')[-1].split('?')[0]
            tender = self.db.get(self.tender_id)
            self.assertIn(key, tender['documents'][-1]["url"])
            self.assertIn('Signature=', tender['documents'][-1]["url"])
            self.assertIn('KeyID=', tender['documents'][-1]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
        else:
            key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        # Get document
        if self.docservice:
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(
                self.tender_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertNotIn('Expires=', response.location)
        else:
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(
                self.tender_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content2')

        # Get document and check response fields
        response = self.app.get('/tenders/{}/documents/{}'.format(self.tender_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name name.doc', response.json["data"]["title"])
        dateModified2 = response.json["data"]['dateModified']
        self.assertTrue(dateModified < dateModified2)
        self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])

        # Get documents with uri param all=true
        response = self.app.get('/tenders/{}/documents?all=true'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified2, response.json["data"][1]['dateModified'])

        # Create new documents, save doc_id, dateModified
        response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        self.assertIn(doc_id, response.headers['Location'])

        # Get documents, and check dateModified
        response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified2, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified, response.json["data"][1]['dateModified'])

        # Try update documents with ivalid fields
        response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, self.tender_token),
                                status=404, upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        # Update document
        response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, self.tender_token),
                                'content3', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        if self.docservice:
            self.assertIn('Signature=', response.json["data"]["url"])
            self.assertIn('KeyID=', response.json["data"]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
            key = response.json["data"]["url"].split('/')[-1].split('?')[0]
            tender = self.db.get(self.tender_id)
            self.assertIn(key, tender['documents'][-1]["url"])
            self.assertIn('Signature=', tender['documents'][-1]["url"])
            self.assertIn('KeyID=', tender['documents'][-1]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
        else:
            key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        # Get document and check response fields
        if self.docservice:
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(
                self.tender_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertNotIn('Expires=', response.location)
        else:
            response = self.app.get('/tenders/{}/documents/{}?download={}'.format(
                self.tender_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content3')

    def test_patch_tender_document(self):
        """
          Test path dialog document
        """
        # Create documents, check response fields and save doc_id
        response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token),
                                 upload_files=[('file', str(Header(u'укр.doc', 'utf-8')), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])

        # Try connect document with lot, without description in params
        response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                      doc_id,
                                                                                      self.tender_token),
                                       {"data": {"documentOf": "lot"}},
                                       status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedItem'},
        ])

        # Try connect document with lot, by bad relatedItem
        response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                      doc_id,
                                                                                      self.tender_token),
                                       {'data': {'documentOf': 'lot', 'relatedItem': '0' * 32}},
                                       status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
        ])

        # Try connect document with item, by bad relatedItem
        response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                      doc_id,
                                                                                      self.tender_token),
                                       {'data': {'documentOf': 'item', 'relatedItem': '0' * 32}},
                                       status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of items'], u'location': u'body', u'name': u'relatedItem'}
        ])

        # Update description in document
        response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                      doc_id,
                                                                                      self.tender_token),
                                       {"data": {"description": "document description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        # Get document and check description
        response = self.app.get('/tenders/{}/documents/{}'.format(self.tender_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])


class DialogUADocumentWithDSResourceTest(DialogUADocumentResourceTest):
    docservice = True


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DialogEUDocumentResourceTest))
    suite.addTest(unittest.makeSuite(DialogEUDocumentWithDSResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
