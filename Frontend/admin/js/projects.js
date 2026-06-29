const projectForm = document.getElementById('projectForm');
const projectList = document.getElementById('projectList');
const imageFileInput = document.getElementById('imageFile');
const uploadImageBtn = document.getElementById('uploadImageBtn');
const imageUploadStatus = document.getElementById('imageUploadStatus');
const gambarUrlInput = document.getElementById('gambar_url');

async function loadProjects() {
    const result = await apiFetch('/projects');
    const items = result.data || [];
    projectList.innerHTML = items.length ? items.map(item => `
        <article class="item">
            <h3>${escapeHtml(item.judul)}</h3>
            <p>${escapeHtml(item.deskripsi)}</p>
            <div class="item-actions">
                <button type="button" onclick='editProject(${JSON.stringify(item)})'>Edit</button>
                <button type="button" class="danger" onclick="deleteProject(${item.id})">Hapus</button>
            </div>
        </article>
    `).join('') : '<p>Belum ada project.</p>';
}

function editProject(item) {
    document.getElementById('itemId').value = item.id;
    document.getElementById('judul').value = item.judul || '';
    document.getElementById('deskripsi').value = item.deskripsi || '';
    gambarUrlInput.value = item.gambar_url || '';
    document.getElementById('link_project').value = item.link_project || '';
    imageUploadStatus.textContent = item.gambar_url ? 'Gambar saat ini sudah tersimpan.' : 'Pilih gambar lalu klik upload.';
}

async function uploadProjectImage() {
    if (!imageFileInput.files.length) {
        imageUploadStatus.textContent = 'Pilih file gambar terlebih dahulu.';
        return;
    }

    const formData = new FormData();
    formData.append('file', imageFileInput.files[0]);

    uploadImageBtn.disabled = true;
    imageUploadStatus.textContent = 'Mengunggah...';

    try {
        const result = await uploadFile('/upload/image', formData);
        gambarUrlInput.value = result.url || '';
        imageUploadStatus.textContent = 'Upload berhasil.';
    } catch (error) {
        imageUploadStatus.textContent = error.message;
    } finally {
        uploadImageBtn.disabled = false;
    }
}

async function deleteProject(id) {
    if (!confirm('Hapus project ini?')) return;
    await apiFetch(`/projects/${id}`, { method: 'DELETE' });
    notifyPortfolioUpdate();
    await loadProjects();
}

projectForm.addEventListener('submit', async event => {
    event.preventDefault();
    const id = document.getElementById('itemId').value;
    await apiFetch(id ? `/projects/${id}` : '/projects', {
        method: id ? 'PUT' : 'POST',
        body: JSON.stringify({
            judul: document.getElementById('judul').value,
            deskripsi: document.getElementById('deskripsi').value,
            gambar_url: gambarUrlInput.value,
            link_project: document.getElementById('link_project').value
        })
    });
    notifyPortfolioUpdate();
    projectForm.reset();
    await loadProjects();
});

document.getElementById('resetBtn').addEventListener('click', () => {
    projectForm.reset();
    gambarUrlInput.value = '';
    imageFileInput.value = '';
    imageUploadStatus.textContent = 'Pilih gambar lalu klik upload.';
});
uploadImageBtn.addEventListener('click', uploadProjectImage);
document.addEventListener('DOMContentLoaded', loadProjects);
