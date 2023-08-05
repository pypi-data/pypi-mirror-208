from ..core.order_discard_reason import OrderDiscardReason
from quick_resto_API.quick_resto_objects.modules.personnel.employee import Employee
from quick_resto_API.quick_resto_objects.modules.front.table_scheme import TableScheme
from quick_resto_API.quick_resto_objects.modules.warehouse.sale_place import SalePlace
from quick_resto_API.quick_resto_objects.quick_resto_object import QuickRestoObject

class Cancellation(QuickRestoObject):
    @property
    def local_create_time(self) -> str:
        return self._local_create_time

    @property
    def local_time_zone_offset_min(self) -> int:
        return self._local_time_zone_offset_min

    @property
    def create_terminal_sale_place_doc_id(self) -> str:
        return self._create_terminal_sale_place_doc_id

    @property
    def create_terminal_sale_place(self) -> SalePlace:
        return self._create_terminal_sale_place

    @property
    def table_scheme_doc_id(self) -> str:
        return self._table_scheme_doc_id

    @property
    def table_scheme(self) -> TableScheme:
        return self._table_scheme

    @property
    def cancellation_reason_doc_id(self) -> str:
        return self._cancellation_reason_doc_id

    @property
    def cancellation_reason(self) -> OrderDiscardReason:
        return self._cancellation_reason

    @property
    def user_doc_id(self) -> str:
        return self._user_doc_id

    @property
    def employee(self) -> Employee:
        return self._employee

    @property
    def table_order_doc_id(self) -> str:
        return self._table_order_doc_id

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def description(self) -> str:
        return self._description

    @property
    def with_dismission(self) -> bool:
        return self._with_dismission

    def __init__(self, version: int = None, serverRegisterTime: str = None, localCreateTime: str = None, localTimeZoneOffsetMin: int = None, 
                    createTerminalSalePlaceDocId: str = None, createTerminalSalePlace: dict = None, tableSchemeDocId: str = None, tableScheme: dict = None, 
                    cancellationReasonDocId: str = None, cancellationReason: dict = None, userDocId: str = None, employee: dict = None, tableOrderDocId: str = None, 
                    comment: str = None, description: str = None, withDismission: bool = None, **kwargs):
        class_name = "ru.edgex.quickresto.modules.front.cancellations.Cancellation"
        super().__init__(class_name=class_name, **kwargs)

        self._version: int = version
        self._server_register_time: str = serverRegisterTime
        self._local_create_time: str = localCreateTime
        self._local_time_zone_offset_min: int = localTimeZoneOffsetMin
        self._create_terminal_sale_place_doc_id: str = createTerminalSalePlaceDocId

        if createTerminalSalePlace is not None: 
            self._create_terminal_sale_place: SalePlace = SalePlace(**createTerminalSalePlace)
        else:
            self._create_terminal_sale_place = None

        self._table_scheme_doc_id: str = tableSchemeDocId

        if tableScheme is not None: 
            self._table_scheme: TableScheme = TableScheme(**tableScheme)
        else:
            self._table_scheme = None

        self._cancellation_reason_doc_id: str = cancellationReasonDocId

        if cancellationReason is not None: 
            self._cancellation_reason: OrderDiscardReason = OrderDiscardReason(**cancellationReason)
        else:
            self._cancellation_reason = None

        self._user_doc_id: str = userDocId

        if employee is not None: 
            self._employee = Employee(**employee)
        else:
            self._employee = None

        self._table_order_doc_id: str = tableOrderDocId
        self._comment: str = comment
        self._description: str = description
        self._with_dismission: bool = withDismission