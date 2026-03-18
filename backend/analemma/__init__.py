"""
Analemma Engine Package

A modular system for calculating and visualizing the analemma - the figure-8 path
the Sun traces in the sky when photographed at the same mean solar time over a year.
"""

from .calculator import AnalemmaCalculator
from .sky_mapper import SkyMapper

__all__ = ['AnalemmaCalculator', 'SkyMapper']
