#  Copyright 2020, 2023 Evandro Chagas Ribeiro da Rosa <evandro@quantuloop.com>
#  Copyright 2020, 2021 Rafael de Santiago <r.santiago@ufsc.br>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from .clib import libs
from .gates import *
from .import_ket import *
from .base import *
from .standard import *
from .process import *
from .gates import __all__ as all_gate
from .import_ket import __all__ as all_import
from .base import __all__ as all_base
from .standard import __all__ as all_standard
from .process import __all__ as all_process

__version__ = '0.6.1rc1'
__all__ = all_gate + all_import + all_base + all_standard + all_process

from .import_ket import code_ket

from .base import QUANTUM_EXECUTION_TARGET
if QUANTUM_EXECUTION_TARGET is None:
    from .kbw import use_sparse
    use_sparse()
