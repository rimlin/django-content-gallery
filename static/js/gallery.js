(function ($) {

    var gallery = (function () {
        var images = [];
        var currentImage = 0;

        var imageSize = null;
        var smallImageSize = null;
        var thumbnailSize = null;

        function getImage(index) {
            currentImage = index;
            if (currentImage >= images.length)
                return null;
            return images[currentImage];
        }

        function getCurrent() {
            return currentImage;
        }

        function getNext() {
            ++currentImage;
            if (currentImage >= images.length)
                currentImage = 0;
            return getCurrent();
        }

        function getPrevious() {
            if (currentImage <= 0)
                currentImage = images.length;
            --currentImage;
            return getCurrent();
        }

        function loadData(app_label, content_type, object_id, callback) {
            currentImage = 0;
            url = "/gallery/ajax/gallery_data/" + app_label + "/" + content_type + "/" + object_id;

            $.ajax({
                url: url,
                dataType: "json",
                beforeSend: function(xhr) {
                    if (xhr.overrideMimeType)
                        xhr.overrideMimeType("application/json");
                },
                success: function (response) {
                    images= response.images;
                    imageSize = response.image_size;
                    smallImageSize = response.small_image_size;
                    thumbnailSize = response.thumbnail_size;
                    callback(images);
                }
            });
        }

        function getImageSize() {
            return imageSize;
        }

        function getSmallImageSize() {
            return smallImageSize;
        }

        function getThumbnailSize() {
            return thumbnailSize;
        }

        function getCount() {
            return images.length;
        }

        return {
            getImage: getImage,
            current: getCurrent,
            next: getNext,
            prev: getPrevious,
            load: loadData,
            getImageSize: getImageSize,
            getSmallImageSize: getSmallImageSize,
            getThumbnailSize: getThumbnailSize,
            count: getCount
        };
    })();

    var galleryView = (function (gallery) {
        var $galleryView,
            $imageContainer,
            $image,
            $thumbnails,
            $scrollLeft,
            $scrollRight,
            $choices,
            $thumbnailsView,
            $imageView,
            $thumbnailsContainer;

        var winWidth, winHeight, thumbnailWidth, maxOffset;
        var animationInProgress = false;
        var ready = false;

        function isSmall() {
            winWidth = $(window).width();
            winHeight = $(window).height();

            return winWidth < gallery.getImageSize().width + 220 ||
                winHeight < gallery.getImageSize().height +
                gallery.getThumbnailSize().height + 85;
        }

        function checkScrollButtons(left) {
            if (left < 0)
                $scrollLeft.removeClass("content_gallery_inactive");
            else
                $scrollLeft.addClass("content_gallery_inactive");

            if (left > maxOffset)
                $scrollRight.removeClass("content_gallery_inactive");
            else
                $scrollRight.addClass("content_gallery_inactive");
        }

        function scrollToImage(index) {
            left = parseInt($thumbnails.css("left"));
            begin = thumbnailWidth * index;
            end = thumbnailWidth * (index + 1);

            if (left + begin >= 0 && left + end <= $thumbnailsContainer.width())
                return;

            animationInProgress = true;

            if (left + begin < 0) {
                newLeft = -begin;
                $thumbnails.animate({left: newLeft}, function () {
                    animationInProgress = false;
                });
            }

            if (left + end > $thumbnailsContainer.width()) {
                newLeft = $thumbnailsContainer.width() - end;
                $thumbnails.animate({left: newLeft}, function () {
                    animationInProgress = false;
                 });
            }
            checkScrollButtons(newLeft);
        }

        function _setImage(index, callback) {
            img = gallery.getImage(index);
            if (!img) return;
            $choices.addClass("choice");
            $($choices[index]).removeClass("choice");
            src = isSmall() ? img.small_image : img.image;
            callback(img, src);
        }

        function setImage(index) {
            _setImage(index, function (img, src) {
                $image.animate({width: 0, height: 0}, function () {
                    $image.attr("src", src);
                    $image.animate({width: img.width, height: img.height});
                });
            });
        }

        function setImageFast(index) {
            _setImage(index, function (img, src) {
                $image.attr("src", src).css({width: img.width, height: img.height});
            });
        }

        function changeImage(index) {
            if (animationInProgress) return;
            setImage(index);
            scrollToImage(index);                
        }

        function setImageViewSize(imgSize) {
            $imageContainer.width(imgSize.width);
            $imageContainer.css({"line-height": imgSize.height + "px"});
            $imageView.height(imgSize.height);
        }

        function setThumbnailViewSize(imgSize, thumbnailSize) {
            $thumbnails.width(thumbnailWidth * gallery.count());

            container_width = Math.ceil(imgSize.width / thumbnailWidth) * thumbnailWidth;
            if (container_width > imgSize.width + 140)
                container_width -= thumbnailWidth;

            $thumbnailsView.width(container_width + 60);
            $choices.width(thumbnailSize.width)
                    .height(thumbnailSize.height)
                    .css("line-height", (thumbnailSize.height - 2) + "px");
            $thumbnailsView.height(thumbnailSize.height + 2);
            $thumbnailsContainer.width(container_width);
        }

        function setGalleryViewSize(imgSize, thumbnailSize) {
            $galleryView.width(imgSize.width + 200);
            $galleryView.height(imgSize.height + thumbnailSize.height + 45);
        }

        function setGalleryViewPosition() {
            galLeft = (winWidth - $galleryView.outerWidth()) / 2;
            galTop = (winHeight - $galleryView.outerHeight()) / 2;

            $galleryView.css({"top": galTop, "left": galLeft});
        }

        function nextImage() {
            index = gallery.next();
            changeImage(index);
        }

        function previousImage() {
           index = gallery.prev();
           changeImage(index);
        }

        function scrollLeft() {
            if (animationInProgress) return;
            left = parseInt($thumbnails.css("left"));
            if (left < 0) {
                animationInProgress = true;
                $thumbnails.animate({left: "+=" + thumbnailWidth}, function () {
                    animationInProgress = false;
                });
            checkScrollButtons(left + thumbnailWidth);
            }
        }

        function scrollRight() {
            if (animationInProgress) return;
            left = parseInt($thumbnails.css("left"));
            if (left > maxOffset) {
                animationInProgress = true;
                $thumbnails.animate({left: "-=" + thumbnailWidth}, function () {
                    animationInProgress = false;
                });
            checkScrollButtons(left - thumbnailWidth);
            }
        }

        function resize() {
            if (!ready) return;

            imgSize = isSmall() ? gallery.getSmallImageSize() : gallery.getImageSize();
            thumbnailSize = gallery.getThumbnailSize()
                
            thumbnailWidth = thumbnailSize.width + 8;

            setImageViewSize(imgSize);
            setThumbnailViewSize(imgSize, thumbnailSize);

            maxOffset = $thumbnailsContainer.width() - $thumbnails.width();

            checkScrollButtons(0);

            setGalleryViewSize(imgSize, thumbnailSize);
            setGalleryViewPosition();

            index = gallery.current();
            setImageFast(index);
        }

        function init(app_label, content_type, object_id) {
            $galleryView = $("#content_gallery_view");
            $imageView = $("#content_gallery_image_view");
            $imageContainer = $(".content_gallery_image_container");
            $image = $(".content_gallery_image_container > img");
            $thumbnailsView = $("#content_gallery_thumbnails_view");
            $scrollLeft = $(".content_gallery_scroll_left");
            $scrollRight = $(".content_gallery_scroll_right");
            $thumbnailsContainer = $(".content_gallery_thumbnails_container");
            $thumbnails = $(".content_gallery_thumbnails_container > ul");

            $thumbnails.on("click", "li", function () {
                setImage($(this).index());
            });

            $(".content_gallery_prev_image").click(previousImage)
            $(".content_gallery_next_image").click(nextImage);
            $scrollLeft.click(scrollLeft);
            $scrollRight.click(scrollRight);

            $thumbnails.empty();

            gallery.load(app_label, content_type, object_id, function (data) {
                $.each(data, function (index, img) {
                    $thumbnails.append($("<li></li>")
                                .addClass("choice")
                                .append($("<img>")
                                    .attr("src", img.thumbnail)
                                    )
                                );
                });

                $choices = $thumbnails.children();

                ready = true;
                resize();

                $("#content_gallery").show();
            });
        }

        return {
            init: init,
            resize: resize
        };
    })(gallery);

    $(window).resize(galleryView.resize);

    $(function () {
        $(".open_gallery").click(function() {
            matches = $(this).attr("id").match(/^gallery-(\w+)-(\w+)-(\d+)$/i);
            if (!matches) return;
            app_label = matches[1];
            content_type = matches[2];
            object_id = matches[3];
            galleryView.init(app_label, content_type, object_id);
        });

        $(".content_gallery_close").click(function() {
            $("#content_gallery").hide();
        });
    });
})(jQuery);