const trs = document.querySelectorAll('#id_filtered_table tr:not(.header)');
const filterTable = () => {
    const filter = document.querySelector('#id_filter_input').value;
    const regex = new RegExp(filter, 'i');
    const isFoundInTds = td => regex.test(td.innerHTML);
    const isFound = childrenArr => childrenArr.some(isFoundInTds);
    const setTrStyleDisplay = ({ style, children }) => {
        style.display = isFound([
            ...children // <-- All columns
        ]) ? '' : 'none'
    }

    trs.forEach(setTrStyleDisplay);
}