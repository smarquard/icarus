function initInfo() {
	console.log("Refreshing");
	showInfo();
	setInterval(function () { showInfo() }, 10000);
	setInterval(function () { refreshMrtgGraphs() }, 150000);
}

function showInfo() {

	// Refresh battery voltage display
	$.ajax({
		url: "http://192.168.100.50:8080/",
		dataType: 'json',
		timeout: 3000,
		error: function(jqXHR, status, errorThrown) {
			console.log("timeout from battery voltage");
			$('#voltage').css({"color":"grey"});
  		}
	}).done( function(data) {
		$('#voltage').html(data.voltage + "V");
		$('#voltage').css({"color":"black"});
	});

        // Refresh mains and inverter power display
        $.ajax({
                url: "http://192.168.100.50:8081/",
                dataType: 'json',
                timeout: 3000,
                error: function(jqXHR, status, errorThrown) {
                        console.log("timeout from power endpoint ");
                        $('#inverter').css({"color":"grey"});
                        $('#grid').css({"color":"grey"});
                }
        }).done( function(data) {
               $('#inverter').html(data.inverter + "W");
               $('#grid').html(data.grid + "W");
               $('#inverter').css({"color":"black"});
               $('#grid').css({"color":"black"});
        });

        // document.title = "solarpi " + data.voltage + "V";

}

function refreshMrtgGraphs() {
  $('.mrtg-voltage img').attr('src', function(i, old) { return old.replace(/\?.+/,"?i=" + (Math.random()*1000)); });
  $('.mrtg-power img').attr('src', function(i, old) { return old.replace(/\?.+/,"?i=" + (Math.random()*1000)); });
}
