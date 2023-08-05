from quick_resto_API.quick_resto_objects.modules.warehouse.cooking_place import CookingPlace
from quick_resto_API.quick_resto_objects.modules.warehouse.dish import Dish
from quick_resto_API.quick_resto_objects.modules.warehouse.modifier import Modifier
from quick_resto_API.quick_resto_objects.modules.warehouse.dish_category import DishCategory
from quick_resto_API.quick_resto_objects.modules.warehouse.sale_place import SalePlace
from quick_resto_API.quick_resto_objects.modules.warehouse.store import Store
from quick_resto_API.quick_resto_objects.quick_resto_object import QuickRestoObject

class OrderItem(QuickRestoObject):
    @property
    def cost_price(self) -> float:
        return self._cost_price

    @property
    def surcharge(self) -> float:
        return self._surcharge

    @property
    def deleted(self) -> bool:
        return self._deleted

    @property
    def price(self) -> float:
        return self._price

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def sale_place(self) -> SalePlace:
        return self._sale_place

    @property
    def seq_number(self) -> int:
        return self._seq_number

    @property
    def product(self) -> Dish | Modifier:
        return self._product

    @property
    def store(self) -> Store:
        return self._store

    @property
    def cost_price_kg(self) -> float:
        return self._cost_price_kg

    @property
    def product_quantity_kg(self) -> float:
        return self._product_quantity_kg

    @property
    def effective_ratio(self) -> float:
        return self._effective_ratio

    @property
    def effective_pack(self) -> float:
        return self._effective_pack

    @property
    def store_item(self) -> Dish | Modifier:
        return self._store_item

    @property
    def cooking_place(self) -> CookingPlace:
        return self._cooking_place

    @property
    def total_price(self) -> float:
        return self._total_price

    @property
    def total_absolute_discount(self) -> float:
        return self._total_absolute_discount

    @property
    def total_absolute_charge(self) -> float:
        return self._total_absolute_charge

    @property
    def total_amount(self) -> float:
        return self._total_amount

    @property
    def name(self) -> str:
        return self._name

    def __init__(self, costPrice: float = None, surcharge: float = None, deleted: bool = None, price: float = None, 
                amount: float = None, salePlace: dict = None, seqNumber: int = None, product: dict = None, store: dict = None, 
                costPriceKg: float = None, productQuantityKg: float = None, effectiveRatio: float = None, effectivePack: float = None, 
                storeItem: dict = None, cookingPlace: dict = None, totalPrice: float = None, totalAbsoluteDiscount: float = None, 
                totalAbsoluteCharge: float = None, totalAmount: float = None, name: str = None, **kwargs):
        class_name = "ru.edgex.quickresto.modules.front.orders.OrderItem"
        super().__init__(class_name=class_name, **kwargs)

        self._cost_price: float = costPrice
        self._surcharge: float = surcharge
        self._deleted: bool = deleted
        self._price: float = price
        self._amount: float = amount
        self._seq_number: int = seqNumber
        self._cost_price_kg: float = costPriceKg
        self._product_quantity_kg: float = productQuantityKg
        self._effective_ratio: float = effectiveRatio
        self._effective_pack: float = effectivePack
        self._total_price: float = totalPrice
        self._total_absolute_discount: float = totalAbsoluteDiscount
        self._total_absolute_charge: float = totalAbsoluteCharge
        self._total_amount: float = totalAmount
        self._name: str = name

        if product is not None:
            if 'Modifier' in product['className']:
                self._product = Modifier(**product)
            elif 'Dish' in product['className']:
                self._product = Dish(**product)
            else:
                self._product = None
        else:
            self._product = None

        if storeItem is not None:
            if 'Modifier' in storeItem['className']:
                self._store_item = Modifier(**product)
            elif 'Dish' in storeItem['className']:
                self._store_item = Dish(**product)
            else:
                self._store_item = None
        else:
            self._store_item = None

        if store is not None:
            self._store = Store(**store)
        else:
            self._store = None

        if salePlace is not None:
            self._sale_place = SalePlace(**salePlace)
        else:
            self._sale_place = None

        if cookingPlace is not None:
            self._cooking_place = CookingPlace(**cookingPlace)
        else:
            self._cooking_place = None