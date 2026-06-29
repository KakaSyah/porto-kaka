const profileFields = [
    'nama_lengkap', 'nama_panggilan', 'tempat_lahir',
    'email', 'telepon', 'universitas', 'fakultas', 'prodi',
    'semester', 'alamat', 'foto_url'
];

function fillProfileForm(profile) {
    profileFields.forEach(field => {
        const input = document.getElementById(field);
        if (input) input.value = profile?.[field] || '';
    });
}

function getProfilePayload() {
    return profileFields.reduce((payload, field) => {
        const input = document.getElementById(field);
        payload[field] = input ? input.value.trim() : '';
        return payload;
    }, {});
}

async function uploadProfilePhoto() {
    const fileInput = document.getElementById('photoFile');
    const uploadButton = document.getElementById('uploadPhotoBtn');
    const status = document.getElementById('photoUploadStatus');
    const fotoUrlInput = document.getElementById('foto_url');

    if (!fileInput.files.length) {
        status.textContent = 'Pilih file foto terlebih dahulu.';
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    uploadButton.disabled = true;
    status.textContent = 'Mengunggah...';

    try {
        const result = await uploadFile('/upload/image', formData);
        fotoUrlInput.value = result.url || '';
        status.textContent = 'Upload berhasil.';
    } catch (error) {
        status.textContent = error.message;
    } finally {
        uploadButton.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('profileForm');
    const message = document.getElementById('profileMessage');
    const uploadButton = document.getElementById('uploadPhotoBtn');
    const status = document.getElementById('photoUploadStatus');

    try {
        const result = await apiFetch('/profiles');
        fillProfileForm(result.data || {});
        const fotoUrl = document.getElementById('foto_url').value;
        status.textContent = fotoUrl ? 'Foto saat ini sudah tersimpan.' : 'Pilih foto lalu klik upload.';
    } catch (error) {
        message.textContent = error.message;
    }

    uploadButton.addEventListener('click', uploadProfilePhoto);

    form.addEventListener('submit', async event => {
        event.preventDefault();
        message.textContent = 'Menyimpan...';

        try {
            const result = await apiFetch('/profiles', {
                method: 'PUT',
                body: JSON.stringify(getProfilePayload())
            });
            fillProfileForm(result.data || {});
            message.textContent = result.message || 'Profil berhasil disimpan';
            notifyPortfolioUpdate();
        } catch (error) {
            message.textContent = error.message;
        }
    });
});
