from fastcrud import FastCRUD

from ...models.collect.variable import Variable
from ...schemas.collect.variable import VariableCreateInternal, VariableDelete, VariableRead, VariableUpdate, VariableUpdateInternal

CRUDVariable = FastCRUD[Variable, VariableCreateInternal, VariableUpdate, VariableUpdateInternal, VariableDelete, VariableRead]
crud_variables = CRUDVariable(Variable)
