/* Apply dselect handling to corresponding classes */
document.querySelectorAll('.dselect').forEach(el => dselect(el))
document.querySelectorAll('.dselect-search').forEach(el => dselect(el, { search: true }))
