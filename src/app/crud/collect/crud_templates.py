from fastcrud import FastCRUD

from ...models.collect.template import Template
from ...schemas.collect.template import TemplateCreateInternal, TemplateDelete, TemplateRead, TemplateUpdate, TemplateUpdateInternal

CRUDTemplate = FastCRUD[Template, TemplateCreateInternal, TemplateUpdate, TemplateUpdateInternal, TemplateDelete, TemplateRead]
crud_templates = CRUDTemplate(Template)
