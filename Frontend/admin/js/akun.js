document.addEventListener('DOMContentLoaded', async () => {
    const passwordMessage = document.getElementById('passwordMessage');

    document.getElementById('passwordForm').addEventListener('submit', async event => {
        event.preventDefault();
        try {
            const result = await apiFetch('/akun/change-password', {
                method: 'POST',
                body: JSON.stringify({
                    old_password: document.getElementById('oldPassword').value,
                    new_password: document.getElementById('newPassword').value
                })
            });
            passwordMessage.textContent = result.message;
            event.target.reset();
        } catch (error) {
            passwordMessage.textContent = error.message;
        }
    });
});
