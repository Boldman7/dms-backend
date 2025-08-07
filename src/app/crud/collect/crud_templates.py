from fastcrud import FastCRUD

from ...models.template import Template
from ...schemas.template import TemplateCreateInternal, TemplateDelete, TemplateRead, TemplateUpdate, TemplateUpdateInternal

CRUDTemplate = FastCRUD[Template, TemplateCreateInternal, TemplateUpdate, TemplateUpdateInternal, TemplateDelete, TemplateRead]
crud_templates = CRUDTemplate(Template)
