..
      Copyright 2010 X7, LLC
      All Rights Reserved.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Image Statuses
==============

Images in Tank can be in one the following statuses:

* ``queued``

  The image identifier has been reserved for an image in the Tank
  registry. No image data has been uploaded to Tank.

* ``saving``

  Denotes that an image's raw data is currently being uploaded to Tank.
  When an image is registered with a call to `POST /images` and there
  is an `x-image-meta-location` header present, that image will never be in
  the `saving` status (as the image data is already available in some other
  location).

* ``active``

  Denotes an image that is fully available in Tank.

* ``killed``

  Denotes that an error occurred during the uploading of an image's data,
  and that the image is not readable.

* ``deleted``

  Tank has retained the information about the image, but it is no longer
  available to use. An image in this state will be removed automatically
  at a later date.

* ``pending_delete``

  This is similiar to `deleted`, however, Tank has not yet removed the
  image data. An image in this state is recoverable.

