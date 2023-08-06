class ErrorViews:

	@staticmethod
	def __render(request, template_name, context):
		from django.shortcuts import render
		return render(request=request, template_name='errors/error_bad_request.html', context={})

	@staticmethod
	def error_400_handler(request, exception):
		return ErrorViews.__render(request=request, template_name='errors/error_bad_request.html', context={})

	@staticmethod
	def error_403_handler(request, exception):
		return ErrorViews.__render(request=request, template_name='errors/error_permission_denied.html',
		                           context={})

	@staticmethod
	def error_404_handler(request, exception):
		from django.http import HttpResponseNotFound
		content_type = 'text/html'
		return HttpResponseNotFound("no found", content_type=content_type)

	@staticmethod
	def error_500_handler(request):
		return ErrorViews.__render(request=request, template_name='errors/error_internal_server.html',
		                           context={})
