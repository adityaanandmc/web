# -*- coding: utf-8 -*-
"""Define the EthOS thumbnail processors.

Copyright (C) 2021 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


def circular_processor(image, circle=False, **kwargs):
    """Force the image to a circle."""
    from .utils import get_circular_image
    if circle:
        image = get_circular_image(image)
    return image
