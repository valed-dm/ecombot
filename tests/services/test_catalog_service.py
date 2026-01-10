from decimal import Decimal
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from ecombot.db.models import Category
from ecombot.db.models import Product
from ecombot.services import catalog_service


async def test_get_all_categories(mocker: MockerFixture, mock_session: AsyncMock):
    """Test fetching all categories."""
    mock_cats = [MagicMock(spec=Category)]
    mock_crud = mocker.patch(
        "ecombot.services.catalog_service.crud.get_categories",
        new_callable=AsyncMock,
        return_value=mock_cats,
    )
    mocker.patch("ecombot.schemas.dto.CategoryDTO.model_validate")

    result = await catalog_service.get_all_categories(mock_session)

    mock_crud.assert_awaited_once_with(mock_session)
    assert len(result) == 1


async def test_add_new_product(mocker: MockerFixture, mock_session: AsyncMock):
    """Test adding a new product."""
    mock_prod = MagicMock(spec=Product)
    mock_create = mocker.patch(
        "ecombot.services.catalog_service.crud.create_product",
        new_callable=AsyncMock,
        return_value=mock_prod,
    )
    mocker.patch("ecombot.schemas.dto.ProductDTO.model_validate")

    await catalog_service.add_new_product(
        mock_session, "Name", "Desc", Decimal("10"), 5, 1
    )

    mock_create.assert_awaited_once()


async def test_update_product_details(mocker: MockerFixture, mock_session: AsyncMock):
    """Test updating product details."""
    mock_prod = MagicMock(spec=Product)
    mock_update = mocker.patch(
        "ecombot.services.catalog_service.crud.update_product",
        new_callable=AsyncMock,
        return_value=mock_prod,
    )
    mocker.patch("ecombot.schemas.dto.AdminProductDTO.model_validate")

    await catalog_service.update_product_details(
        mock_session, 10, {"price": Decimal("20")}
    )

    mock_update.assert_awaited_once_with(mock_session, 10, {"price": Decimal("20")})
