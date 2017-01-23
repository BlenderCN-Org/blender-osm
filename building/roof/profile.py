"""
This file is part of blender-osm (OpenStreetMap importer for Blender).
Copyright (C) 2014-2017 Vladimir Elistratov
prokitektura+support@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import math
from mathutils import Vector
from . import Roof
from util import zero
from util.osm import parseNumber


# Use https://raw.githubusercontent.com/wiki/vvoovv/blender-osm/assets/roof_profiles.blend
# to generate values for a specific profile
gabledRoof = (
    (
        (0., 0.),
        (0.5, 1.),
        (1., 0.)
    ),
    {
        "numSamples": 10,
        "angleToHeight": 0.5
    }
)

roundRoof = (
    (
        (0., 0.),
        (0.01, 0.195),
        (0.038, 0.383),
        (0.084, 0.556),
        (0.146, 0.707),
        (0.222, 0.831),
        (0.309, 0.924),
        (0.402, 0.981),
        (0.5, 1.),
        (0.598, 0.981),
        (0.691, 0.924),
        (0.778, 0.831),
        (0.854, 0.707),
        (0.916, 0.556),
        (0.962, 0.383),
        (0.99, 0.195),
        (1., 0.)
    ),
    {
        "numSamples": 1000,
        "angleToHeight": None
    }
)

gambrelRoof = (
    (
        (0., 0.),
        (0.2, 0.6),
        (0.5, 1.),
        (0.8, 0.6),
        (1., 0.)
    ),
    {
        "numSamples": 10,
        "angleToHeight": None
    }
)

saltboxRoof = (
    (
        (0., 0.),
        (0.35, 1.),
        (0.65, 1.),
        (1., 0.)
    ),
    {
        "numSamples": 100,
        "angleToHeight": 0.35
    }
)


class ProfiledVert:
    """
    A class represents a vertex belonging to RoofProfile.polygon projected on the profile
    """
    def __init__(self, roof, i, roofMinHeight, noWalls):
        """
        Args:
            roof (RoofProfile): an instance of the class <RoofProfile>
            i (int): index (between 0 and <roof.polygon.n-1>) of the polygon vertex
            roofMinHeight (float): Supplied by BuildingRenderer.renderElement(..)
            noWalls (bool): Does the building has wallls?
        """
        self.i = i
        verts = roof.verts
        indices = roof.polygon.indices
        proj = roof.projections
        p = roof.profile
        d = roof.direction
        v = verts[indices[i]]
        onProfile = False
        createVert = True
        # Coordinate along roof profile (i.e. along the roof direction)
        # the roof direction is calculated in roof.processDirection(..);
        # the coordinate can possess the value from 0. to 1.
        x = (proj[i] - proj[roof.minProjIndex]) / roof.polygonWidth
        # Coordinate (with an offset) across roof profile;
        # a perpendicular to <roof.direction> is equal to <Vector((-d[1], d[0], 0.))
        self.y = -v[0]*d[1] + v[1]*d[0]
        # index in <roof.profileQ>
        index = roof.profileQ[
            math.floor(x * roof.numSamples)
        ]
        distance = x - p[index][0]
        # check if x is equal zero
        if distance < zero:
            onProfile = True
            if roof.lEndZero and noWalls and not index:
                createVert = False
                index = 0
                x = 0.
                vertIndex = indices[i]
            else:
                x, h = p[index]
        elif abs(p[index + 1][0] - x) < zero:
            onProfile = True
            # increase <index> by one
            index += 1
            if roof.rEndZero and noWalls and index == roof.lastProfileIndex:
                createVert = False
                index = roof.lastProfileIndex
                x = 1.
                vertIndex = indices[i]
            else:
                x, h = p[index]
        else:
            h1 = p[index][1]
            h2 = p[index+1][1]
            h = h1 + (h2 - h1) / (p[index+1][0] - p[index][0]) * distance
        if createVert:
            vertIndex = len(verts)
            verts.append(Vector((v.x, v.y, roofMinHeight + roof.h * h)))
        self.index = index
        self.onProfile = onProfile
        self.x = x
        self.vertIndex = vertIndex


class Slot:
    
    def __init__(self):
        # (y, chunk, reflection)
        self.parts = []
        self.partsR = []
        # does a part from <self.parts> with <index> end at self (True) or at neighbor slot (False) 
        self.endAtSelf = []
    
    def reset(self):
        self.parts.clear()
        self.partsR.clear()
        self.endAtSelf.clear()
        # the current index in <self.parts>
        self.index = 0
    
    def prepare(self):
        self.parts.sort(key = lambda p: p[0])
    
    def append(self, vertIndex, y=None, originSlot=None, reflection=None):
        parts = self.parts
        if y is None:
            parts[-1][1].append(vertIndex)
        else:
            parts.append((y, [vertIndex], reflection, self.index))
            originSlot.endAtSelf.append(originSlot is self)
            self.index += 1
    
    def trackDown(self, roofIndices, index=None, destVertIndex=None):
        parts = self.parts
        indexPartR = -1
        index = (len(parts) if index is None else index) - 2
        vertIndex0 = None
        while index >= 0:
            _, part, reflection, _index = parts[index]
            if vertIndex0 is None:
                vertIndex0 = parts[index+1][1][0]
                roofFace = []
            # <False> for the reflection means reflection to the left
            if reflection is False:
                index -= 1
                continue
            roofFace.extend(part)
            if part[-1] == vertIndex0:
                # came up and closed the loop
                roofIndices.append(roofFace)
                vertIndex0 = None
            elif not self.endAtSelf[_index]:
                # came to the neighbor from the right
                roofFace.extend(self.n.partsR[indexPartR])
                indexPartR -= 1
                roofIndices.append(roofFace)
                vertIndex0 = None
            elif part[-1] != parts[index-1][1][0]:
                index = self.trackDown(roofIndices, index, part[-1])
            if not destVertIndex is None and parts[index-1][1][0] == destVertIndex:
                return index
            # <True> for the reflection means reflection to the right
            index -= 1 if reflection is True else 2

    def trackUp(self, roofIndices, index=None, destVertIndex=None):
        parts = self.parts
        numParts = len(parts)
        index = 1 if index is None else index+2
        vertIndex0 = None
        while index < numParts:
            _, part, reflection, _index = parts[index]
            if vertIndex0 is None:
                vertIndex0 = parts[index-1][1][0]
                roofFace = []
            # <True> for the reflection means reflection to the right
            if reflection is True:
                index += 1
                continue
            roofFace.extend(part)
            if part[-1] == vertIndex0:
                # came down and closed the loop
                roofIndices.append(roofFace)
                vertIndex0 = None
            elif not self.endAtSelf[_index]:
                # came to the neighbor from the left
                self.partsR.append(roofFace)
                vertIndex0 = None
            elif part[-1] != parts[index+1][1][0]:
                    index = self.trackUp(roofIndices, index, part[-1])
            if not destVertIndex is None and parts[index+1][1][0] == destVertIndex:
                return index
            # <False> for the reflection means reflection to the left
            index += 1 if reflection is False else 2
    
    def processWallFace(self, indices, pv1, pv2):
        """
        A child class may provide realization for this methods
        
        Args:
            indices (list): Vertex indices for the wall face
            pv1 (ProfiledVert): the first vertex of the two between which the slot vertex is located
            pv2 (ProfiledVert): the second vertex of the two between which the slot vertex is located
        """
        pass


class RoofProfile(Roof):
    """
    The class deals with so called profiled roofs (i.e. roofs defined be a profile):
    gabled, round, gambrel, saltbox
    
    See https://github.com/vvoovv/blender-osm/wiki/Profiled-roofs for description and illustration
    of concepts and algorithms used in the code. Specifically, the image <Main> from that webpage is
    used a number of times to illustrate the code.
    """
    
    defaultHeight = 3.
    
    def __init__(self, data):
        """
        Args:
            data (tuple): profile values and some attributes to define a profiled roof,
                e.g. gabledRoof, roundRoof, gambrelRoof, saltboxRoof
        """
        super().__init__()
        self.hasRidge = True
        self.projections = []
        
        # actual profile values as a Python tuple of (x, y)
        profile = data[0]
        self.profile = profile
        numProfilesPoints = len(profile)
        self.lastProfileIndex = numProfilesPoints - 1
        # create profile slots
        slots = tuple(Slot() for i in range(numProfilesPoints) )
        # set the next slot, it will be need in further calculations
        for i in range(self.lastProfileIndex):
            slots[i].n = slots[i+1]
        self.slots = slots
        
        for attr in data[1]:
            setattr(self, attr, data[1][attr])
        
        # is the y-coordinate at <x=0.0> (the left end of the profile) is equal to zero?
        self.lEndZero = not profile[0][1]
        # is the y-coordinate at <x=1.0> (the right end of the profile) is equal to zero?
        self.rEndZero = not profile[-1][1]
        
        # Quantize <profile> with <numSamples> to get performance gain
        # Quantization is needed to perform the following action very fast.
        # Given x-coordinate <x> between 0. and 1. in the profile coordinate system,
        # find two neighboring slots between which <x> is located
        _profile = tuple(math.ceil(p[0]*self.numSamples) for p in profile)
        profileQ = []
        index = 0
        for i in range(self.numSamples):
            if i >= _profile[index+1]:
                index += 1  
            profileQ.append(index)
        profileQ.append(index)
        self.profileQ = profileQ

    def init(self, element, minHeight, osm):
        super().init(element, minHeight, osm)
        self.initProfile()
    
    def initProfile(self):
        self.projections.clear()
        # The last slot with the index <self.lastProfileIndex> isn't touched,
        # so no need to reset it
        for i in range(self.lastProfileIndex):
            self.slots[i].reset()
    
    def make(self, bldgMaxHeight, roofMinHeight, bldgMinHeight, osm):
        polygon = self.polygon
        roofIndices = self.roofIndices
        noWalls = bldgMinHeight is None
        slots = self.slots
        # the current slot: start from the leftmost slot
        self.slot = slots[0]
        # the slot from which the last part in <slot.parts> originates
        self.originSlot = slots[0]
        
        if not self.projections:
            self.processDirection()
        
        # Start with the vertex from <polygon> with <x=0.> in the profile coordinate system;
        # the variable <i0> is needed to break the cycle below
        i = i0 = self.minProjIndex
        # Create a profiled vertex out of <self.verts[polygon.indices[i]]>;
        # <pv> stands for profiled vertex
        pv1 = pv0 = ProfiledVert(self, i, roofMinHeight, noWalls)
        _pv = None
        while True:
            i = polygon.next(i)
            if i == i0:
                # came to the starting vertex, so break the cycle
                break
            # create a profiled vertex out of <self.verts[polygon.indices[i]]>
            pv2 = ProfiledVert(self, i, roofMinHeight, noWalls)
            # The order of profiled vertices is <_pv>, <pv1>, <pv2>
            # Create in-between vertices located on the slots for the segment between <pv1> and <pv2>)
            self.createProfileVertices(pv1, pv2, _pv, roofMinHeight, noWalls)
            _pv = pv1     
            pv1 = pv2
        # Create in-between vertices located on the slots for the closing segment between <pv1> and <pv0>
        self.createProfileVertices(pv1, pv0, _pv, roofMinHeight, noWalls)
        
        # Append the vertices from the first part of the <slot[0]> (i.e. slots[0].parts[0])
        # to the last part of <slots[1]> (i.e. slots[1].parts[-1])
        # Example on the image <Main>:
        # slots[0].parts[0][1] is [11, 12, 15]
        # slots[1].parts[-1][1] is [28, 11]
        # after the execution of the line of below:
        # slots[1].parts[-1][1] is [28, 11, 12, 15]
        slots[1].parts[-1][1].extend(slots[0].parts[0][1][i] for i in range(1, len(slots[0].parts[0][1])))
        # the last part of <slots[1]> ends at self
        slots[1].endAtSelf.append(True)
        
        # Prepare the slots to form faces for the roof;
        # note that slots[0] and slots[-1] aren't used in calculations
        for i in range(1, self.lastProfileIndex):
            slots[i].prepare()
        
        # Below is the cycle to form faces for the roof
        # Each time a band between the neighboring slots
        # <slotL> (a slot from the left) and <slotR> (a slot from the right) is considered.
        # We trace <slotR> upwards by executing <slotR.trackUp(roofIndices)>,
        # then we trace <slotL> downwards by executing slotL.trackDown(roofIndices)
        slotR = slots[1]
        slotR.trackUp(roofIndices)
        for i in range(1, self.lastProfileIndex):
            slotL = slotR
            slotR = slots[i+1]
            slotR.trackUp(roofIndices)
            slotL.trackDown(roofIndices)
        return True
    
    def createProfileVertices(self, pv1, pv2, _pv, roofMinHeight, noWalls):
        """
        Create in-between vertices located on the slots for the segment between <pv1> and <pv2>
        """
        verts = self.verts
        indices = self.polygon.indices
        p = self.profile
        wallIndices = self.wallIndices
        slots = self.slots
        slot = self.slot
        
        index1 = pv1.index
        index2 = pv2.index
            
        skip1 = noWalls and pv1.onProfile and\
            ((self.lEndZero and not index1) or\
            (self.rEndZero and index1 == self.lastProfileIndex))
        skip2 = noWalls and pv2.onProfile and\
            ((self.lEndZero and not index2) or\
            (self.rEndZero and index2 == self.lastProfileIndex))

        if skip1 and skip2 and index1 == index2:
            if _pv is None:
                slot.append(pv1.vertIndex, pv1.y, self.originSlot)
            slot.append(pv2.vertIndex)
            return
        _wallIndices = [pv1.vertIndex]
        if not skip1:
            _wallIndices.append(indices[pv1.i])
        if not skip2:
            _wallIndices.append(indices[pv2.i])
        _wallIndices.append(pv2.vertIndex)
        
        v1 = verts[indices[pv1.i]]
        v2 = verts[indices[pv2.i]]
        if not _pv is None:
            _v = verts[indices[_pv.i]]
        
        # deal with the roof top
        if _pv is None:
            slot.append(pv1.vertIndex, pv1.y, self.originSlot)
        elif pv1.onProfile:
            reflection = None
            appendToSlot = False
            if pv2.onProfile and index1 == index2:
                if (_pv.x < pv1.x and pv1.y > pv2.y) or (_pv.x > pv1.x and pv1.y < pv2.y):
                    appendToSlot = True
            elif pv1.x < pv2.x:
                # going from the left to the right
                if _pv.x < pv1.x:
                    appendToSlot = True
                elif index1:
                    # The condition <index1> is to prevent
                    # erroneous reflection due to zero angle as the result of mapping error or
                    # precision error caused by the nature of <zero> variable
                    if _pv.onProfile and _pv.index == pv1.index:
                        if _pv.y < pv1.y:
                            appendToSlot = True
                            # no reflection in this case!
                    elif (pv2.x-pv1.x)*(_pv.y-pv1.y) - (pv2.y-pv1.y)*(_pv.x-pv1.x) < 0.:
                        appendToSlot = True
                        # <True> for the reflection means reflection to the right
                        reflection = True
            else:
                # going from the right to the left
                if _pv.x > pv1.x:
                    appendToSlot = True
                elif index1 != self.lastProfileIndex:
                    # The condition <index1 != self.lastProfileIndex> is to prevent
                    # erroneous reflection due to zero angle as the result of mapping error or
                    # precision error caused by the nature of <zero> variable
                    if _pv.onProfile and _pv.index == pv1.index:
                        if _pv.y > pv1.y:
                            appendToSlot = True
                            # no reflection in this case!
                    elif (pv2.x-pv1.x)*(_pv.y-pv1.y) - (pv2.y-pv1.y)*(_pv.x-pv1.x) < 0.:
                        appendToSlot = True
                        # <False> for the reflection means reflection to the left
                        reflection = False
            if appendToSlot:
                self.originSlot = slot
                slot = slots[index1]
                slot.append(pv1.vertIndex, pv1.y, self.originSlot, reflection)
        
        def common_code(slot, vertsRange, slotRange):
            """
            A helper function
            """
            vertIndex = len(verts) - 1
            factorX = (v2.x - v1.x) / (pv2.x - pv1.x)
            factorY = (v2.y - v1.y) / (pv2.x - pv1.x)
            for _i in vertsRange:
                vertIndex += 1
                factor = p[_i][0] - pv1.x
                verts.append(Vector((
                    v1.x + factor * factorX,
                    v1.y + factor * factorY,
                    roofMinHeight + self.h * p[_i][1]
                )))
                _wallIndices.append(vertIndex)
            # fill <slots>
            factor = (pv2.y - pv1.y) / (pv2.x - pv1.x)
            for _i in slotRange:
                slot.append(vertIndex)
                self.originSlot = slot
                slot = slots[_i]
                slot.append(vertIndex, pv1.y + factor * (p[_i][0] - pv1.x), self.originSlot)
                slot.processWallFace(_wallIndices, pv1, pv2)
                vertIndex -= 1
            return slot
        
        if index1 != index2:
            if index2 > index1:
                if not pv2.onProfile or index1 != index2-1:
                    slot = common_code(
                        slot,
                        range(index2-1 if pv2.onProfile else index2, index1, -1),
                        range(index1+1, index2 if pv2.onProfile else index2+1)
                    )
            else:
                if not pv1.onProfile or index2 != index1-1:
                    slot = common_code(
                        slot,
                        range(index2+1, index1 if pv1.onProfile else index1+1),
                        range(index1-1 if pv1.onProfile else index1, index2, -1)
                    )
        wallIndices.append(_wallIndices)
        slot.append(pv2.vertIndex)
        self.slot = slot
    
    def getHeight(self, op):
        tags = self.element.tags
        
        h = parseNumber(tags["roof:height"]) if "roof:height" in tags else None
        if h is None:
            if not self.angleToHeight is None and "roof:angle" in tags:
                angle = parseNumber(tags["roof:angle"])
                if not angle is None:
                    self.processDirection()
                    h = self.angleToHeight * self.polygonWidth * math.tan(math.radians(angle))
            if h is None:
                # getting the number of levels
                if "roof:levels" in tags:
                    h = parseNumber(tags["roof:levels"])
                h = self.defaultHeight if h is None else h * op.levelHeight
        self.h = h
        return h