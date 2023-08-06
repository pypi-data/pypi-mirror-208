from rest_framework import renderers, status


class CustomJSONRenderer(renderers.JSONRenderer):
    """
    This is a custom JSON renderer that extends the default JSONRenderer provided by Django REST framework.
    It is used to generate JSON responses in a standardized format with a consistent structure that includes the status code, message, and either data or errors depending on the response status.

    The render method takes in three arguments:

    data: the data to be rendered as JSON
    accepted_media_type: the media type accepted by the client
    renderer_context: a dictionary containing information about the renderer and the response
    The method first retrieves the response object from the renderer context and extracts the data and errors attributes from the input data dictionary.
    Then, it creates a JSON response dictionary with the status code and message attributes from the response and adds the data attribute if the response is successful, or the errors attribute if the response is not successful.
    Finally, it calls the render method of the parent JSONRenderer class with the updated JSON response dictionary, the accepted media type, and the renderer context, and returns the result.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response")
        data_attr = data.get('data', {})
        error_attr = data.get('errors', [])
        json_response = {
            'status': response.status_code,
            'message': data['message'],
            'data': data_attr,
            'errors': error_attr
        }
        return super().render(json_response, accepted_media_type, renderer_context)
