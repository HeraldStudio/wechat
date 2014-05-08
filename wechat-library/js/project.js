jQuery(document).ready(function($) {
	$('#submit').click(function() {
		$.ajax({
			url: 'http://121.248.63.105/herald_web_service/library/search_book/',
			type: 'GET',
			dataType: 'text',
			data: {'strText': 'java'},
			success: function(data){
				console.log(data);
			},
			error:function(){
				console.log('ss');
			}
		})
	});
});