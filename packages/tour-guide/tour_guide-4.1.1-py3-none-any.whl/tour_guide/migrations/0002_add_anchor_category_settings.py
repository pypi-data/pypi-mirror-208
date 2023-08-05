from django.db import migrations, transaction


def define_default_layout_roles(apps, schema_editor):

    # noinspection PyPep8Naming
    AnchorCategorySetting = apps.get_model('tour_guide', 'AnchorCategorySetting')
    DEFAULT_NUMBER_FORMAT = 'tour_guide:numbers'
    LETTERS_NUMBER_FORMAT = 'tour_guide:letters'
    DEFAULT_IDENTIFIER_FORMAT = 'tour_guide:generic'
    ANCHOR_IDENTIFIER_FORMAT = 'tour_guide:anchor_identifier'

    with transaction.atomic():
        figure_category = AnchorCategorySetting()
        figure_category.name = 'Figure'
        figure_category.identifier = 'figure'
        figure_category.label = 'Figure'
        figure_category.label_plural = 'Figures'
        figure_category.label_short = 'Fig'
        figure_category.number_format = DEFAULT_NUMBER_FORMAT
        figure_category.identifier_format = DEFAULT_IDENTIFIER_FORMAT
        figure_category.save()

        image_category = AnchorCategorySetting()
        image_category.name = 'Image'
        image_category.identifier = 'image'
        image_category.label = 'Image'
        image_category.label_plural = 'Images'
        image_category.label_short = 'Img'
        image_category.number_format = DEFAULT_NUMBER_FORMAT
        image_category.identifier_format = DEFAULT_IDENTIFIER_FORMAT
        image_category.save()

        table_category = AnchorCategorySetting()
        table_category.name = 'Table'
        table_category.identifier = 'table'
        table_category.label = 'Table'
        table_category.label_plural = 'Tables'
        table_category.label_short = 'T'
        table_category.number_format = DEFAULT_NUMBER_FORMAT
        table_category.identifier_format = DEFAULT_IDENTIFIER_FORMAT
        table_category.save()

        equation_category = AnchorCategorySetting()
        equation_category.name = 'Equation'
        equation_category.identifier = 'equation'
        equation_category.label = 'Equation'
        equation_category.label_plural = 'Equations'
        equation_category.label_short = 'Eq'
        equation_category.number_format = DEFAULT_NUMBER_FORMAT
        equation_category.identifier_format = DEFAULT_IDENTIFIER_FORMAT
        equation_category.save()

        listing_category = AnchorCategorySetting()
        listing_category.name = 'Code Listing'
        listing_category.identifier = 'listing'
        listing_category.label = 'Listing'
        listing_category.label_plural = 'Listings'
        listing_category.label_short = 'L'
        listing_category.number_format = DEFAULT_NUMBER_FORMAT
        listing_category.identifier_format = DEFAULT_IDENTIFIER_FORMAT
        listing_category.save()

        section_category = AnchorCategorySetting()
        section_category.name = 'Section'
        section_category.identifier = 'section'
        section_category.label = 'Section'
        section_category.label_plural = 'Section'
        section_category.label_short = 'Sec'
        section_category.number_format = DEFAULT_NUMBER_FORMAT
        section_category.identifier_format = ANCHOR_IDENTIFIER_FORMAT
        section_category.save()

        slideshow_category = AnchorCategorySetting()
        slideshow_category.name = 'Slideshow'
        slideshow_category.identifier = 'slideshow'
        slideshow_category.label = 'Slideshow'
        slideshow_category.label_plural = 'Slideshow'
        slideshow_category.label_short = 'Slideshow'
        slideshow_category.number_format = DEFAULT_NUMBER_FORMAT
        slideshow_category.identifier_format = DEFAULT_IDENTIFIER_FORMAT
        slideshow_category.save()

        reference_category = AnchorCategorySetting()
        reference_category.name = 'Reference'
        reference_category.identifier = 'ref'
        reference_category.label = ''
        reference_category.label_plural = ''
        reference_category.label_short = ''
        reference_category.number_format = LETTERS_NUMBER_FORMAT
        reference_category.identifier_format = DEFAULT_IDENTIFIER_FORMAT
        reference_category.save()

        endnote_category = AnchorCategorySetting()
        endnote_category.name = 'Endnote'
        endnote_category.identifier = 'endnote'
        endnote_category.label = ''
        endnote_category.label_plural = ''
        endnote_category.label_short = ''
        endnote_category.link_css_class = 'endnote-link'
        endnote_category.label_css_class = 'endnote-label'
        endnote_category.number_format = DEFAULT_NUMBER_FORMAT
        endnote_category.identifier_format = DEFAULT_IDENTIFIER_FORMAT
        endnote_category.save()

        aside_category = AnchorCategorySetting()
        aside_category.name = 'Aside'
        aside_category.identifier = 'aside'
        aside_category.label = ''
        aside_category.label_plural = ''
        aside_category.label_short = ''
        endnote_category.link_css_class = 'aside-link'
        endnote_category.label_css_class = 'aside-label'
        aside_category.number_format = DEFAULT_NUMBER_FORMAT
        aside_category.identifier_format = DEFAULT_IDENTIFIER_FORMAT
        aside_category.save()

        generic_category = AnchorCategorySetting()
        generic_category.name = 'Generic'
        generic_category.identifier = 'generic'
        generic_category.label = ''
        generic_category.label_plural = ''
        generic_category.label_short = ''
        generic_category.number_format = DEFAULT_NUMBER_FORMAT
        generic_category.identifier_format = ANCHOR_IDENTIFIER_FORMAT
        generic_category.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tour_guide', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(define_default_layout_roles),
    ]
