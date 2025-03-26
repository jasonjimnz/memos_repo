import datetime
import os
import uuid

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, \
    send_from_directory  # Add current_app, send_from_directory
from flask_login import current_user, login_required  # Import login_required
from werkzeug.utils import secure_filename

from . import db  # Import db instance
from .models import Memo, Resource  # Import Memo model
from .forms import MemoForm  # Import MemoForm

bp = Blueprint('main', __name__)
# Define max file size (e.g., 50MB) - reuse this
MAX_FILE_SIZE = 50 * 1024 * 1024

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = MemoForm()
    if form.validate_on_submit():
        # 1. Create Memo object (without saving yet)
        memo = Memo(content=form.content.data, creator_id=current_user.id)

        # --- 2. Handle MULTIPLE file uploads ---
        files = request.files.getlist(form.resource_files.name) # Get list of files
        resource_records = [] # Store records to be associated later

        for file in files:
            if file and file.filename != '': # Check if a file was actually uploaded
                try:
                    original_filename = secure_filename(file.filename)

                    # Check file size
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    if file_size > MAX_FILE_SIZE:
                       flash(f'File "{original_filename}" exceeds size limit ({MAX_FILE_SIZE // (1024*1024)}MB).', 'warning')
                       continue # Skip this file

                    # Generate unique internal filename
                    _, file_ext = os.path.splitext(original_filename)
                    internal_filename = str(uuid.uuid4()) + file_ext
                    mime_type = file.mimetype

                    # Save file
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], internal_filename)
                    file.save(file_path)

                    # Create Resource DB record (without memo_id yet)
                    resource = Resource(
                        creator_id=current_user.id,
                        filename=original_filename,
                        internal_filename=internal_filename,
                        type=mime_type,
                        size=file_size,
                        memo_id=None # Explicitly None for now
                    )
                    db.session.add(resource)
                    resource_records.append(resource) # Add to list for later association

                except Exception as e:
                    # Log the error for debugging
                    current_app.logger.error(f"Error uploading file {original_filename}: {e}")
                    flash(f'Error uploading file "{original_filename}".', 'danger')
                    # Continue to next file, or decide if the whole process should fail

        # --- 3. Save Memo and associate Resources ---
        try:
            db.session.add(memo)
            db.session.flush() # Get memo.id

            # Associate all successfully uploaded resources
            for resource in resource_records:
                resource.memo_id = memo.id

            db.session.commit() # Commit memo and all associated resources
            flash('Your memo and any attached files have been saved!', 'success')

        except Exception as e:
            db.session.rollback() # Rollback transaction on error
            current_app.logger.error(f"Error saving memo or associating resources: {e}")
            flash(f'Error saving memo: {e}', 'danger')
            # Need to consider deleting already saved files if the DB commit fails
            for resource in resource_records:
                 try:
                     file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resource.internal_filename)
                     if os.path.exists(file_path):
                        os.remove(file_path)
                 except Exception as cleanup_error:
                     current_app.logger.error(f"Error cleaning up file {resource.internal_filename} after DB error: {cleanup_error}")


        return redirect(url_for('main.index')) # Redirect after POST

    # --- GET Request Handling ---
    # ... (keep existing code to fetch and display memos) ...
    user_memos = Memo.query.filter_by(creator_id=current_user.id).order_by(Memo.created_ts.desc()).all()
    return render_template('index.html', title='Home', form=form, memos=user_memos)

# --- Add Edit Memo Route ---
@bp.route('/memo/<int:memo_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_memo(memo_id):
    # Fetch the memo by ID, or return 404 if not found
    memo = Memo.query.get_or_404(memo_id)

    # Authorization check: Ensure the current user is the creator of the memo
    if memo.creator_id != current_user.id:
        abort(403)  # Forbidden error if not the owner

    # Use the same MemoForm
    form = MemoForm()

    if form.validate_on_submit():  # This runs on POST request after validation
        # Update memo content and timestamp
        memo.content = form.content.data
        memo.updated_ts = datetime.datetime.utcnow()  # Update the timestamp
        db.session.commit()  # Commit changes to the database
        flash('Your memo has been updated!', 'success')
        return redirect(url_for('main.index'))  # Redirect back to the homepage
    elif request.method == 'GET':  # This runs on GET request
        # Pre-populate the form with the existing memo content
        form.content.data = memo.content

    # Render the edit template for both GET and failed POST validation
    return render_template('edit_memo.html', title='Edit Memo', form=form, memo=memo)


# --- Add Delete Memo Route ---
@bp.route('/memo/<int:memo_id>/delete', methods=['POST'])  # Only allow POST requests
@login_required
def delete_memo(memo_id):
    # Fetch the memo by ID, or return 404 if not found
    memo = Memo.query.get_or_404(memo_id)

    # Authorization check: Ensure the current user is the creator of the memo
    if memo.creator_id != current_user.id:
        abort(403)  # Forbidden error if not the owner

    # Delete the memo from the database session
    db.session.delete(memo)
    # Commit the transaction to permanently remove it
    db.session.commit()

    flash('Your memo has been deleted.', 'success')
    return redirect(url_for('main.index'))  # Redirect back to the homepage


@bp.route('/uploads/<filename>')
@login_required  # Protect access to uploads
def uploaded_file(filename):
    # Need to check if the current user has permission to view this file!
    # Find the resource record by internal_filename
    resource = Resource.query.filter_by(internal_filename=filename).first_or_404()

    # Basic check: Is the current user the creator of the resource OR the creator of the memo it's attached to?
    # More complex visibility rules would be needed later.
    if resource.creator_id != current_user.id:
        if not resource.memo or resource.memo.creator_id != current_user.id:
            # Or check memo visibility if implementing public/protected memos
            abort(403)  # Forbidden

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# --- Add Delete Resource Route ---
@bp.route('/resource/<int:resource_id>/delete', methods=['POST'])
@login_required
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)

    # Authorization Check: Allow if user created the resource OR created the memo it's attached to
    if resource.creator_id != current_user.id:
        if not resource.memo or resource.memo.creator_id != current_user.id:
            abort(403) # Forbidden

    # Construct file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resource.internal_filename)

    try:
        # Delete physical file first
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            # Log or flash a warning if file was already missing, but proceed to delete DB record
            current_app.logger.warning(f"Physical file not found for resource {resource.id} at {file_path}, but deleting DB record.")

        # Delete DB record
        db.session.delete(resource)
        db.session.commit()
        flash(f'Attachment "{resource.filename}" deleted successfully.', 'success')

    except Exception as e:
        db.session.rollback() # Rollback DB change if file deletion failed unexpectedly after check
        current_app.logger.error(f"Error deleting resource {resource.id}: {e}")
        flash(f'Error deleting attachment "{resource.filename}".', 'danger')

    # Redirect back to index (or potentially memo detail page if you implement one)
    return redirect(url_for('main.index'))
# --- End Delete Resource Route ---
