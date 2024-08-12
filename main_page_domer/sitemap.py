from django.contrib.sitemaps import Sitemap

from advertisement.models import Category  

  
  
class CategorySitemap(Sitemap):  
    changefreq = 'id'
    priority = 0.9
  
    def items(self):  
        return Category.objects.all()  
      
    def lastmod(self, obj):  
        return obj.parent_id
