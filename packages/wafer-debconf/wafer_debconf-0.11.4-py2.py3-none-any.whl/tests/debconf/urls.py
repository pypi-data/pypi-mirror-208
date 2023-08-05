from django.conf.urls import include, url


urlpatterns = [
    url(r'^badges/', include('badges.urls')),
    url(r'^bursary/', include('bursary.urls')),
    url(r'^front_desk/', include('front_desk.urls')),
    url(r'^invoices/', include('invoices.urls')),
    url(r'^register/', include('register.urls')),

    url(r'', include('debconf.urls')),
    url(r'', include('exports.urls')),
    url(r'', include('wafer.urls')),
]
