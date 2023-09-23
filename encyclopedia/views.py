from django.shortcuts import render
from . import util
from markdown2 import Markdown
import random
from django.urls import reverse
from django.http import HttpResponseRedirect
import re


entries = util.list_entries()   

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": entries
    })

def entry(request, entry):
    # If required a random entry trough GET
    if request.method == 'GET':
        if request.GET.get('rand',''):
            entry = str(random.choice(entries))

            return HttpResponseRedirect(reverse('entry', args=(entry,))) 

    try:
        # Gets markdown from entry title, then render
        markdown = Markdown().convert(util.get_entry(entry))
        return render(request, "encyclopedia/entry.html", {
            "title": entry,
            "entry": markdown
        })
    except:
        # On invalid url entry, show 404 error 
        return render(request, "encyclopedia/entry.html", {
            "error": "404 not found"
        })
 
def search(request):
    if request.method == 'GET':
        query = request.GET.get('q','')

        # Search for a coincidence case insensitive
        if query.lower() in [entry.lower() for entry in entries]:
            return HttpResponseRedirect(reverse('entry', args=(query,))) 
        else:
            results = []

            # Search for substrings case insensitive and append to results list 
            for entry in entries:
                if query.lower() in entry.lower():
                    results.append(entry)

            return render(request, "encyclopedia/search.html", {
                "entries": results
            })

def new(request):
    # TODO: Use form class model
    if request.method == 'POST':
        # If an entry was sent
        if request.POST.get('title','') and request.POST.get('markdown',''):
            title = request.POST.get('title','')
            markdown = request.POST.get('markdown','')

            # If entry already exists render error and the form
            global entries
            if title in entries:
                return render(request, "encyclopedia/new.html", {
                    "error": "Entry already exists."
                })
            else:
                # If doesn't exists, creates entry, update entries list and redirects to the new page
                util.save_entry(title, markdown)
                entries = util.list_entries()   
                return HttpResponseRedirect(reverse('entry', args=(title,))) 
        else:
            # If empty inputs render error
            return render(request, "encyclopedia/new.html", {
                "error": "All fields are required."
            })

    return render(request, "encyclopedia/new.html")


def edit(request, entry):
    if request.method == 'POST':
        # If the entry was edited
        # Validate inputs
        if request.POST.get('title','') == entry and request.POST.get('markdown',''):
            # elminimating extra white space in markdown
            markdown = request.POST.get('markdown','')
            cleaned_markdown = re.sub('\n{3,}|\r|\t', '', markdown).strip(' \r\n\t')

            util.save_entry(entry, cleaned_markdown)
            return HttpResponseRedirect(reverse('entry', args=(entry,)))
        else:
            # If invalid input
            # If a markdown was sent, return it to the form, else, check file markdown
            markdown = request.POST.get('markdown','') if request.POST.get('markdown','') else util.get_entry(entry)
            
            return render(request, "encyclopedia/edit.html", {
                "entry": entry,
                "content": markdown,
                "error": "Invalid input"
            })

    else:
        # Populate the form with a clean markdown (elminimating extra white space)
        markdown = util.get_entry(entry)
        cleaned_markdown = re.sub('\n{3,}|\r|\t', '', markdown).strip(' \r\n\t')

        return render(request, "encyclopedia/edit.html", {
            "entry": entry,
            "content": cleaned_markdown
        })