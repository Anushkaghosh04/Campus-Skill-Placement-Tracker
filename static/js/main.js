document.addEventListener('DOMContentLoaded', function () {
    var toggleBtn = document.getElementById('sidebarToggle');
    var sidebar = document.getElementById('sidebar');
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }

    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert').forEach(function (alertEl) {
        setTimeout(function () {
            var alert = bootstrap.Alert.getOrCreateInstance(alertEl);
            alert.close();
        }, 5000);
    });
});
