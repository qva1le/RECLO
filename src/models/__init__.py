from src.database import Base

# Сначала те модели, на которые ссылаются другие
from .attributes import AttributesOrm

# Потом уже значения атрибутов
from .product_attribute_values import ProductAttributesValuesOrm

# Потом продукты, т.к. они ссылаются на ProductAttributesValuesOrm
from .products import ProductsOrm

# Потом всё остальное
from .product_reviews import ProductReviewsOrm
from .product_fires import ProductFiresOrm

# И остальные твои модели
# from .users import UsersOrm
# from .shops import ShopsOrm
# ...
