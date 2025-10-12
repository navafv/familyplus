import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files.base import ContentFile
from store.models import Product, ProductGallery # Make sure to import from your app name
from category.models import Category

class Command(BaseCommand):
    """
    Django management command to import products from DummyJSON API.

    This command fetches product data from the specified URL, processes it,
    and populates the Product and Category models in the database.
    It handles creating categories with descriptions and images, downloading 
    and saving product images, and generating slugs.
    """
    help = 'Imports products from the DummyJSON API into the database.'

    # The API endpoint to fetch products from
    API_URL = "https://dummyjson.com/products?select=title,price,category,description,images,stock&limit=194"

    def handle(self, *args, **options):
        """
        The main logic for the command.
        """
        self.stdout.write(self.style.SUCCESS('Starting product import process...'))

        try:
            # Make a request to the API
            response = requests.get(self.API_URL)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()
            products_data = data.get('products', [])
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Failed to fetch data from API: {e}'))
            return

        if not products_data:
            self.stdout.write(self.style.WARNING('No products found in the API response.'))
            return

        # Counter for successfully imported products
        created_count = 0

        for item in products_data:
            # Skip if product with the same name already exists to avoid duplicates
            if Product.objects.filter(product_name__iexact=item['title']).exists():
                self.stdout.write(self.style.WARNING(f"Product '{item['title']}' already exists. Skipping."))
                continue

            try:
                # --- 1. Get or Create Category ---
                category_name = item['category'].replace('-', ' ').title()
                category_slug = slugify(category_name)
                # Add a generated description to the defaults for creation
                category, created = Category.objects.get_or_create(
                    category_name=category_name,
                    defaults={
                        'slug': category_slug,
                        'description': f"A collection of great products in the {category_name} category."
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created new category: '{category_name}'"))

                # --- 2. Create Product Instance ---
                product = Product(
                    product_name=item['title'],
                    slug=slugify(item['title']),
                    description=item['description'],
                    price=int(item['price']), # The model expects an IntegerField
                    stock=item['stock'],
                    is_available=True,
                    category=category,
                )

                # --- 3. Handle Main Product Image and Category Image ---
                images = item.get('images', [])
                if images:
                    image_url = images[0]
                    try:
                        img_response = requests.get(image_url)
                        img_response.raise_for_status()
                        
                        image_name = image_url.split("/")[-1]
                        image_content = ContentFile(img_response.content)
                        
                        # Save the main image to the Product model (but don't save the model yet)
                        product.images.save(image_name, image_content, save=False)

                        # If we just created the category, assign this product's image as the category image
                        if created:
                            category_image_content = ContentFile(img_response.content)
                            category.cat_image.save(image_name, category_image_content, save=True)
                            self.stdout.write(self.style.SUCCESS(f"  - Assigned '{image_name}' as the image for new category '{category_name}'."))

                    except requests.exceptions.RequestException as img_e:
                        self.stdout.write(self.style.ERROR(f"Could not download image for '{item['title']}': {img_e}"))
                
                # --- 4. Save the Product ---
                product.save()

                # --- 5. Handle Product Gallery Images ---
                if len(images) > 1:
                    for gallery_image_url in images[1:]:
                        try:
                            gallery_img_response = requests.get(gallery_image_url)
                            gallery_img_response.raise_for_status()

                            gallery_image_name = gallery_image_url.split("/")[-1]
                            gallery_image_content = ContentFile(gallery_img_response.content)

                            product_gallery = ProductGallery(product=product)
                            product_gallery.image.save(gallery_image_name, gallery_image_content, save=True)
                            self.stdout.write(self.style.SUCCESS(f"  - Added gallery image: {gallery_image_name}"))

                        except requests.exceptions.RequestException as gallery_img_e:
                            self.stdout.write(self.style.ERROR(f"  - Could not download gallery image for '{item['title']}': {gallery_img_e}"))
                
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Successfully processed product: '{product.product_name}'"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"An error occurred while creating product '{item['title']}': {e}"))

        self.stdout.write(self.style.SUCCESS(f'\nProduct import complete! Successfully created {created_count} new products.'))

