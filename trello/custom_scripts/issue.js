frappe.ui.form.on('Issue', {
    // on refresh event
    trello_board(frm) {
        if(frm.doc.trello_board){
            frappe.call('trello.api.get_board_list', {
                board_id: frm.doc.board_id
            }).then(r => {
                console.log(r.message)
                $.each(r.message, function(key, value) {   
                    $('select[data-fieldname="board_list"]').append($("<option></option>").attr("value", value.name).text(value.name)); 
               });
            })
            frm.fields_dict['board_list'].get_query = function(doc) {
                return {
                    filters: {
                        "board_id": frm.doc.board_id
                    }
                }
            }
        }
    }
})