$(document).ready(function() {
    $("#resizable").resizable({
        handles: "e",
        minWidth: 100,
        maxWidth: 600,
    });

    $("#selectable").selectable(
    {
        filter: "li",
        selecting: function(event, ui){
            var rest = $(".ui-selected").not(ui.selecting).removeClass("ui-selected");
            $(".list-asset").not(".ui-selected").css({"background-color":"white", "border":""});
        },
        stop: function() {
            var selected = $(".ui-selectee.ui-selected");
            var selectedSymbol = selected.data("symbol");

            selected.css({"border":"2px solid black"});
            $(".list-asset").not(".ui-selected").css("background-color", "white");
            console.log(selectedSymbol);
            if (selectedSymbol != null)
            {
                $.ajax({
                    type: "POST",
                    url:"handle_selection", // La URL se genera correctamente aquí
                    contentType: "application/json",
                    data: JSON.stringify({ selected_symbol: selectedSymbol }),
                    success: function(response) {
                        console.log("Server response:", response);
                    },
                    error: function(error) {
                        console.error("Error:", error);
                    }
                });
            }
        }
    });

    $(".list-asset").hover(
        function() {
            if (!$(this).hasClass("ui-selected")) {
                $(this).css("background-color", "lightblue");
            }
        },
        function() {
            if (!$(this).hasClass("ui-selected")) {
                $(this).css("background-color", "white");
            }
        }
    );
    
    $(document).on("mouseup", function() {
        $("list-asset:not(.ui-selected)").css({"background-color":"white", "border":""});
    });
});
