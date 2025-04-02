from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import os
import uuid
from app import db, cache
from app.models import Page, Tag, Media, PageVersion
from app.forms import PageForm, MediaUploadForm, TagForm

# Create blueprint
content = Blueprint('content', __name__)

@content.route('/pages')
@cache.cached(timeout=60)  # Cache for 1 minute
def pages():
    """Display list of published pages"""
    pages = Page.query.filter_by(is_published=True).order_by(Page.created_at.desc()).all()
    return render_template('content/pages.html', title='Pages', pages=pages)

@content.route('/page/<slug>')
@cache.cached(timeout=60, unless=lambda: current_user.is_authenticated)  # Cache for 1 minute, unless user is logged in
def page(slug):
    """Display a single page by slug"""
    page = Page.query.filter_by(slug=slug).first_or_404()

    # If page is not published, only allow author or admin to view
    if not page.is_published and (not current_user.is_authenticated or
                                 (current_user.id != page.user_id and not current_user.is_admin())):
        abort(404)

    return render_template('content/page.html', title=page.title, page=page)

@content.route('/page/new', methods=['GET', 'POST'])
@login_required
def create_page():
    """Create a new page"""
    form = PageForm()

    # Get all available tags for the form
    form.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()]

    if form.validate_on_submit():
        page = Page(
            title=form.title.data,
            slug=form.slug.data,
            content=form.content.data,
            summary=form.summary.data,
            is_published=form.is_published.data,
            user_id=current_user.id
        )

        # Handle featured image if provided
        if form.featured_image.data:
            filename = save_media(form.featured_image.data, 'image')
            page.featured_image = filename

        # Add selected tags
        selected_tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
        page.tags = selected_tags

        # Set published date if publishing
        if form.is_published.data:
            page.published_at = datetime.now(timezone.utc)

        db.session.add(page)
        db.session.commit()

        # Create initial page version
        version = PageVersion(
            page_id=page.id,
            content=page.content,
            title=page.title,
            user_id=current_user.id
        )
        db.session.add(version)
        db.session.commit()

        flash('Your page has been created!', 'success')
        return redirect(url_for('content.page', slug=page.slug))

    return render_template('content/create_page.html', title='New Page', form=form, legend='New Page')

@content.route('/page/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_page(slug):
    """Edit an existing page"""
    page = Page.query.filter_by(slug=slug).first_or_404()

    # Check if user is authorized to edit (author or admin)
    if page.user_id != current_user.id and not current_user.is_admin():
        abort(403)

    form = PageForm()
    form.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()]

    if form.validate_on_submit():
        # Create a page version before updating
        version = PageVersion(
            page_id=page.id,
            content=page.content,
            title=page.title,
            user_id=current_user.id
        )
        db.session.add(version)

        # Update page
        page.title = form.title.data
        page.slug = form.slug.data
        page.content = form.content.data
        page.summary = form.summary.data

        # Handle published status change
        if not page.is_published and form.is_published.data:
            page.published_at = datetime.now(timezone.utc)
        page.is_published = form.is_published.data

        # Handle featured image if provided
        if form.featured_image.data:
            filename = save_media(form.featured_image.data, 'image')
            page.featured_image = filename

        # Update tags
        selected_tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
        page.tags = selected_tags

        page.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        flash('Your page has been updated!', 'success')
        return redirect(url_for('content.page', slug=page.slug))

    elif request.method == 'GET':
        # Populate form with existing data
        form.title.data = page.title
        form.slug.data = page.slug
        form.content.data = page.content
        form.summary.data = page.summary
        form.is_published.data = page.is_published
        form.tags.data = [tag.id for tag in page.tags]

    return render_template('content/create_page.html', title='Edit Page',
                          form=form, legend='Edit Page')

@content.route('/page/<slug>/delete', methods=['POST'])
@login_required
def delete_page(slug):
    """Delete a page"""
    page = Page.query.filter_by(slug=slug).first_or_404()

    # Check if user is authorized to delete (author or admin)
    if page.user_id != current_user.id and not current_user.is_admin():
        abort(403)

    # Delete all versions first (due to foreign key constraints)
    PageVersion.query.filter_by(page_id=page.id).delete()

    db.session.delete(page)
    db.session.commit()

    flash('Your page has been deleted!', 'success')
    return redirect(url_for('content.pages'))

@content.route('/page/<slug>/versions')
@login_required
def page_versions(slug):
    """View page version history"""
    page = Page.query.filter_by(slug=slug).first_or_404()

    # Check if user is authorized to view versions (author or admin)
    if page.user_id != current_user.id and not current_user.is_admin():
        abort(403)

    versions = PageVersion.query.filter_by(page_id=page.id).order_by(PageVersion.created_at.desc()).all()

    return render_template('content/page_versions.html', title='Page History',
                          page=page, versions=versions)

@content.route('/page/<slug>/version/<int:version_id>')
@login_required
def page_version(slug, version_id):
    """View a specific page version"""
    page = Page.query.filter_by(slug=slug).first_or_404()
    version = PageVersion.query.filter_by(id=version_id, page_id=page.id).first_or_404()

    # Check if user is authorized to view versions (author or admin)
    if page.user_id != current_user.id and not current_user.is_admin():
        abort(403)

    return render_template('content/page_version.html', title='Page Version',
                          page=page, version=version)

@content.route('/page/<slug>/restore/<int:version_id>', methods=['POST'])
@login_required
def restore_version(slug, version_id):
    """Restore a page to a previous version"""
    page = Page.query.filter_by(slug=slug).first_or_404()
    version = PageVersion.query.filter_by(id=version_id, page_id=page.id).first_or_404()

    # Check if user is authorized to restore versions (author or admin)
    if page.user_id != current_user.id and not current_user.is_admin():
        abort(403)

    # Create a new version with current content before restoring
    current_version = PageVersion(
        page_id=page.id,
        content=page.content,
        title=page.title,
        user_id=current_user.id
    )
    db.session.add(current_version)

    # Restore content from selected version
    page.content = version.content
    page.title = version.title
    page.updated_at = datetime.now(timezone.utc)

    db.session.commit()

    flash('Page has been restored to the selected version!', 'success')
    return redirect(url_for('content.page', slug=page.slug))

@content.route('/media')
@login_required
def media_library():
    """Display media library"""
    media_files = Media.query.filter_by(user_id=current_user.id).order_by(Media.created_at.desc()).all()
    return render_template('content/media_library.html', title='Media Library', media_files=media_files)

@content.route('/media/upload', methods=['GET', 'POST'])
@login_required
def upload_media():
    """Upload media files"""
    form = MediaUploadForm()

    if form.validate_on_submit():
        filename = save_media(form.file.data, form.file_type.data)

        # Create media record
        media = Media(
            filename=filename,
            original_filename=form.file.data.filename,
            file_type=form.file_type.data,
            file_size=len(form.file.data.read()),
            file_extension=os.path.splitext(form.file.data.filename)[1][1:].lower(),
            path=f"uploads/{form.file_type.data}/{filename}",
            alt_text=form.alt_text.data,
            user_id=current_user.id
        )

        db.session.add(media)
        db.session.commit()

        flash('Your file has been uploaded!', 'success')
        return redirect(url_for('content.media_library'))

    return render_template('content/upload_media.html', title='Upload Media', form=form)

@content.route('/tags')
@login_required
@cache.cached(timeout=300)  # Cache for 5 minutes
def tags():
    """Display list of tags"""
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('content/tags.html', title='Tags', tags=tags)

@content.route('/tag/<tag_name>')
@cache.cached(timeout=60)  # Cache for 1 minute
def tag_pages(tag_name):
    """Display pages with a specific tag"""
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    pages = Page.query.filter(Page.tags.contains(tag), Page.is_published==True).all()

    return render_template('content/tag_pages.html', title=f'Tag: {tag.name}',
                          tag=tag, pages=pages)

@content.route('/tag/new', methods=['GET', 'POST'])
@login_required
def create_tag():
    """Create a new tag"""
    form = TagForm()

    if form.validate_on_submit():
        tag = Tag(name=form.name.data)
        db.session.add(tag)
        db.session.commit()

        flash('Your tag has been created!', 'success')
        return redirect(url_for('content.tags'))

    return render_template('content/create_tag.html', title='New Tag', form=form)

@content.route('/tag/<tag_name>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_name):
    """Edit an existing tag"""
    tag = Tag.query.filter_by(name=tag_name).first_or_404()

    # Only admin can edit tags
    if not current_user.is_admin():
        abort(403)

    form = TagForm()

    if form.validate_on_submit():
        tag.name = form.name.data
        db.session.commit()

        flash('Tag has been updated!', 'success')
        return redirect(url_for('content.tags'))

    elif request.method == 'GET':
        form.name.data = tag.name

    return render_template('content/create_tag.html', title='Edit Tag', form=form)

@content.route('/tag/<tag_name>/delete', methods=['POST'])
@login_required
def delete_tag(tag_name):
    """Delete a tag"""
    tag = Tag.query.filter_by(name=tag_name).first_or_404()

    # Only admin can delete tags
    if not current_user.is_admin():
        abort(403)

    db.session.delete(tag)
    db.session.commit()

    flash('Tag has been deleted!', 'success')
    return redirect(url_for('content.tags'))

def save_media(file_data, file_type):
    """Save uploaded media file to the appropriate directory"""
    # Generate a unique filename
    filename = str(uuid.uuid4()) + os.path.splitext(file_data.filename)[1]

    # Ensure upload directory exists
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', file_type)
    os.makedirs(upload_dir, exist_ok=True)

    # Save the file
    file_path = os.path.join(upload_dir, filename)
    file_data.save(file_path)

    return filename
