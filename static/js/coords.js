function sendCoordsToServer(coords) {
    $.ajax({
        type: "POST",
        url: "/main",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            lat: coords.latitude,
            long: coords.longitude
        }),
        success: function (locale) {
            $('#locale-alert').alert();
            console.log('Hi')
            updateLocaleDropdown(locale);
        }
    })
}

function updateLocaleDropdown(new_locale) {
    $('#locale-dropdown').selectpicker('val', new_locale);
}

if('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
        position => {
            sendCoordsToServer(position.coords);
        },
        _ => {
            sendCoordsToServer({
                lat: null,
                long: null
            })
        }
    )
} else {
    console.log("Geolocation not available.")
}
