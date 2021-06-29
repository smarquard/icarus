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
		timeout: 5000,
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
		// Show solar if non-zero
		if (data.inverter > 0) {
			$('#inverter_static').html("");
			$('#inverter_label').html("Solar ");
			$('#inverter').html(data.inverter + "W");
			$('#inverter').css({"color":"black"});
        		document.title = "solarpi " + data.inverter + "W / " + data.grid + "W";
		} else {
			$('#inverter_label').html("");
			$('#inverter').html("");
			$('#inverter_static').html("");
        		document.title = "solarpi " + data.grid + "W";
		}

		// Always show grid
		$('#grid').html(data.grid + "W");
		$('#grid').css({"color":"black"});
        });

}

function refreshMrtgGraphs() {
  $('.mrtg-voltage img').attr('src', function(i, old) { return old.replace(/\?.+/,"?i=" + (Math.random()*1000)); });
  $('.mrtg-power img').attr('src', function(i, old) { return old.replace(/\?.+/,"?i=" + (Math.random()*1000)); });
}
