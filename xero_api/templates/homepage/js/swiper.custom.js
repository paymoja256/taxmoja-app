/*------------------------------------------------------------------
Initialize Swiper
-------------------------------------------------------------------*/
"use strict";
var swiper = new Swiper('.testimonials', {
  speed: 600,
  parallax: true,
  pagination: {
	el: '.swiper-pagination',
	dynamicBullets: true,
	clickable : true
  },
});