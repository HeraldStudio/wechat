var page=1;
var val;
jQuery(document).ready(function($) {
	$('#submit').click(function() {
		val = $("#search")[0].value;
		$.ajax({
			url: 'http://herald.seu.edu.cn/herald_web_service/library/search_book/',
			type: 'GET',
			dataType: 'text',
			data: {'strText': val},
			success: function(data){
				var responseResult= $.parseJSON(data);
				$('#headertitle h1').html('我心仪的书单');
				$('#searchform').remove();
				var book = '';
				$.each(responseResult, function(index, val) {
					var num = index+1;
					book += '<tr>'+
		             '<th>'+num+'</th>'+
		             '<td>'+val.title+'</td>'+
		             '<td>'+val.author+'</td>'+
		             '<td>'+val.isbn+'</td>'+
		             '<td>'+val.store_num+'</td>'+
		           '</tr>';
				});

				var addHtml = '<table>'+
		         '<thead>'+
		           '<tr class="ui-bar-d">'+
		             '<th>序号</th>'+
		             '<th>书籍名称</th>'+
		             '<th>作者</th>'+
		             '<th>索书号</th>'+
		             '<th>馆存数量</th>'+
		           '</tr>'+
		         '</thead>'+
		         '<tbody>';
		         addHtml += book + '</tbody></table>';
				$('#searchresult').append(addHtml);
				$('#getmore').append('<a href="#" id="more">查看更多</a>');
			}
		})
	});
	$(document).on('click', '#more', function() {
		page+=1;
		$.ajax({
			url: 'http://herald.seu.edu.cn/herald_web_service/library/search_book/',
			type: 'GET',
			dataType: 'text',
			data: {'strText': val,'page':page},
			success:function(data){
				alert(val);

			}
		})
		
		
	});
});