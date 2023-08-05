/**
 * Check whether the user is logged in on the AlekSIS server.
 *
 * @param {Object} whoAmI The person object as returned by the whoAmI query
 * @returns true if the user is logged in, false if not
 */
const notLoggedInValidator = (whoAmI) => {
  return !whoAmI || whoAmI.isAnonymous;
};

const hasPersonValidator = (whoAmI) => {
  return whoAmI && whoAmI.person && !whoAmI.person.isDummy;
};

export { notLoggedInValidator, hasPersonValidator };
