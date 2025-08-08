from fastcrud import FastCRUD

from ...models.variable import Variable
from ...schemas.variable import VariableCreateInternal, VariableDelete, VariableRead, VariableUpdate, VariableUpdateInternal

CRUDVariable = FastCRUD[Variable, VariableCreateInternal, VariableUpdate, VariableUpdateInternal, VariableDelete, VariableRead]
crud_variables = CRUDVariable(Variable)
