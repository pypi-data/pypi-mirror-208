from PySide6.QtCore import QObject
from loguru import logger

from ..enums import SizePolicy, Alignment
from ..types import Applicable, Size


class SizedObj(SizePolicy):
    @staticmethod
    def Sizes(
            *,
            vpolicy: SizePolicy = None,
            hpolicy: SizePolicy = None,

            # margins: ? = ?,
            # padding: ? = ?,
            alignment: Alignment.Alignment = Alignment.Left,

            size: Size = None,
            width: int = None,
            height: int = None,

            min_size: Size = None,
            min_width: int = None,
            min_height: int = None,

            max_size: Size = None,
            max_width: int = None,
            max_height: int = None,

            fixed_size: Size = None,
            fixed_width: int = None,
            fixed_height: int = None
    ) -> Applicable:
        async def apply(self: QObject):
            nonlocal vpolicy, hpolicy
            policy = self.sizePolicy()
            if not vpolicy:
                vpolicy = policy.verticalPolicy()
            if not hpolicy:
                hpolicy = policy.verticalPolicy()
            self.setSizePolicy(vpolicy, hpolicy)

            if hasattr(self, 'alignment'):
                self.setAlignment(alignment)

            if size:
                self.resize(size.size)
                if width or height:
                    logger.warning(self.__warning)
            elif width:
                self.resize(width, self.height())
            elif height:
                self.resize(self.width(), height)

            if min_size:
                self.setMinimumSize(min_size.size)
                if min_width or min_height:
                    logger.warning(self.__warning)
            elif min_width:
                self.setMinimumWidth(min_width)
            elif min_height:
                self.setMinimumHeight(min_height)

            if max_size:
                self.setMaximumSize(max_size.size)
                if max_width or max_height:
                    logger.warning(self.__warning)
            elif max_width:
                self.setMaximumWidth(max_width)
            elif max_height:
                self.setMaximumHeight(max_height)

            if fixed_size:
                self.setFixedSize(fixed_size.size)
                if fixed_width or fixed_height:
                    logger.warning(self.__warning)
            elif fixed_width:
                self.setFixedWidth(fixed_width)
            elif fixed_height:
                self.setFixedHeight(fixed_height)
            return self
        return apply

    @property
    def __warning(self) -> str:
        return f'Review `{self.objectName()}.sized()` arguments'

