# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2011 X7 LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import engine
from engine import utils
from engine import flags
from engine.image import tank

FLAGS = flags.FLAGS


def get_default_image_service():
    ImageService = utils.import_class(FLAGS.image_service)
    return ImageService()


def get_image_service(context, image_href):
    """Get the proper image_service and id for the given image_href.

    The image_href param can be an href of the form
    http://mytankserver:9292/images/42, or just an int such as 42. If the
    image_href is an int, then the default image service is returned.

    :param image_href: image ref/id for an image
    :returns: a tuple of the form (image_service, image_id)

    """
    # check if this is not a uri
    if '/' not in str(image_href):
        return (get_default_image_service(), image_href)

    else:
        (tank_client, image_id) = tank.get_tank_client(context,
                                                             image_href)
        image_service = engine.image.tank.TankImageService(tank_client)
        return (image_service, image_id)
