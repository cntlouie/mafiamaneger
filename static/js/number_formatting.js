function formatNumber(number) {
    return new Intl.NumberFormat().format(number);
}

function parseFormattedNumber(formattedNumber) {
    return parseInt(formattedNumber.replace(/,/g, ''), 10);
}

// Add event listeners to format numbers on input
document.addEventListener('DOMContentLoaded', function() {
    const numberInputs = document.querySelectorAll('input[type="text"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            const value = e.target.value.replace(/,/g, '');
            if (!isNaN(value) && value.trim() !== '') {
                e.target.value = formatNumber(parseInt(value, 10));
            }
        });
    });
});
