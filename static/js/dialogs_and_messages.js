// Выделение диалогов в ЛК поштучно либо сразу всех
let select_all = document.getElementById('select_dialogs');
let checkboxes = document.getElementsByName('dialog_checkbox');

select_all.addEventListener('change', select_all_dialogs);

function select_all_dialogs(event) {
    for (let i = 0; i < checkboxes.length; i++) {

}


checkboxes[i].checked = event.target.checked;
}
}

for (let i = 0; i < checkboxes.length; i++) {
checkboxes[i].addEventListener('change', find_unchecked_dialogs)
}

function find_unchecked_dialogs(event) {
for (let i = 0; i < checkboxes.length; i++) {
if (checkboxes[i].checked == false) {
select_all.checked = false;
break;
}
select_all.checked = true;
}