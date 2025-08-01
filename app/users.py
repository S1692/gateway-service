"""
User management endpoints.

This router demonstrates how to create and fetch users using Supabase.  It
leverages Supabase Auth for registration and queries the `users` table for
retrieving profile information.  Error handling is minimal and should be
extended to suit your application’s needs.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from .database import get_supabase


router = APIRouter()


class UserCreate(BaseModel):
    """
    Schema used to validate user creation requests.

    `pydantic`'s `EmailStr` type is not used here to avoid the optional
    dependency on `email-validator`.  If you require stricter validation,
    consider adding `email_validator` to your dependencies and changing the
    type annotation back to `EmailStr`.
    """

    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Account password")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    supabase=Depends(get_supabase),
) -> dict[str, Any]:
    """
    Register a new user via Supabase Auth.

    Parameters
    ----------
    user : UserCreate
        The user credentials to register.
    supabase : supabase.Client
        Injected Supabase client.

    Returns
    -------
    dict[str, Any]
        A JSON response containing a user ID and email on success.
    """

    # Sign up the user using Supabase Auth.  The response includes user data
    # and a session object on success, or an error object on failure.
    result = supabase.auth.sign_up({"email": user.email, "password": user.password})
    # The supabase-py client returns a dictionary with either 'error' or 'user'
    error = result.get("error")
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "An unknown error occurred during sign up"),
        )

    user_data = result.get("user")
    # Save additional profile information in the public users table.  Some
    # applications choose to store profile data separately from the auth
    # metadata for greater flexibility.  Here we simply ensure a row exists.
    supabase.table("users").insert({
        "id": user_data["id"],
        "email": user_data["email"],
    }).execute()

    return {"id": user_data["id"], "email": user_data["email"]}


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    supabase=Depends(get_supabase),
) -> dict[str, Any]:
    """
    Retrieve a single user profile from the Supabase database.

    Parameters
    ----------
    user_id : str
        Unique identifier of the user to fetch.
    supabase : supabase.Client
        Injected Supabase client.

    Returns
    -------
    dict[str, Any]
        The user profile or an error message if not found.
    """
    result = supabase.table("users").select("*").eq("id", user_id).single().execute()
    if result.error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.error.message,
        )
    return result.data