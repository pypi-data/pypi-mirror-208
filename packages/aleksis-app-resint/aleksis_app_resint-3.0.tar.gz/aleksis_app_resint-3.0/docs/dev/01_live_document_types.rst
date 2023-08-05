Providing live document types from other apps
=============================================

AlekSIS apps can provide live document types that
are then managed by Resint. Live document types are
Django models sub-classing the ``LiveDocument`` model,
and providing fields and some methods that define how
the live document is generated.

The following stripped-down example shows how to
provide a live document type.

.. code-block:: python

   from aleksis.apps.resint.models import LiveDocument

   class AutomaticPlan(LiveDocument):
       # Template name to render
       template = "my_app/pdf_template.html"

       # A field to be rendered in the edit form
       number_of_days = models.PositiveIntegerField(
           default=1,
       )

       def get_context_data(self) -> Dict[str, Any]:
           """Get context data to pass to the PDF template."""
	   context = {}
	   # Do something ehre to construct the context data
	   return context

This basic example generates a PDF by defining an HTML template
and overriding the ``get_context_data`` method. This method has
to return a context dictionary, which will then be passed to
the template.

If you need more control over how the PDF is generated, you
can instead override the ``update`` method:

.. code-block:: python

   class AutomaticPlan(LiveDocument):
       def update(self, triggered_manually: bool = True):
           """Re-generate PDF for this live document."""

	   # Do whatever is necessary to get file contents

	   self.current_file.save(self.filename, content)

You need to ensure that ``update()`` is called whenever you
need to provide a new version of your document. One possibility
is to listen to some relevant DJango signal, then call ``update()``
if necessary.
